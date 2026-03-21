import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).resolve().parents[2]
backend_root = project_root / "backend"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.services.oasis_profile_generator import OasisAgentProfile
from app.services.ops_memory_store import load_agent_state, save_agent_state


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REQUIRED_KEYS = (
    "emotion",
    "action",
    "shares_news",
    "influences_count",
    "post_content",
)

STATE_SIGNAL_KEYS = (
    "government_targeted",
    "government_relief_positive",
    "fear_triggered",
    "positive_outcome",
    "public_exposure",
)

FORBIDDEN_COMMODITY_TERMS = (
    "চিনি",
    "sugar",
    "তেল",
    "oil",
    "গম",
    "wheat",
    "ডাল",
    "lentil",
)


def load_profile(profile_path: Path) -> OasisAgentProfile:
    with profile_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        if not data:
            raise ValueError(f"No profiles found in {profile_path}")
        data = data[0]

    return OasisAgentProfile.from_dict(data)


def scenario_targets_rice(scenario: str) -> bool:
    scenario_lower = scenario.lower()
    return "rice" in scenario_lower or "চাল" in scenario


def strip_code_fences(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json_payload(content: str) -> dict[str, Any]:
    cleaned = strip_code_fences(content)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(cleaned[start:end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Model output is not a JSON object.")

    return parsed


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    working = dict(payload)

    post_content = working.get("post_content")
    if isinstance(post_content, dict):
        for key in ("bangla", "text", "content", "post_content"):
            value = post_content.get(key)
            if isinstance(value, str) and value.strip():
                working["post_content"] = value
                break

    shares_news = working.get("shares_news")
    if isinstance(shares_news, str):
        lowered = shares_news.strip().lower()
        if lowered in {"true", "false"}:
            working["shares_news"] = lowered == "true"

    influences_count = working.get("influences_count")
    if isinstance(influences_count, str):
        try:
            working["influences_count"] = int(influences_count.strip())
        except ValueError:
            pass

    for key in ("emotion", "action"):
        value = working.get(key)
        if isinstance(value, str):
            cleaned = re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")
            working[key] = cleaned or value.strip()

    if isinstance(working.get("post_content"), str):
        working["post_content"] = re.sub(r"\s+", " ", working["post_content"]).strip()

    return {key: working.get(key) for key in REQUIRED_KEYS}


def validate_payload(payload: dict[str, Any], profile: dict[str, Any], scenario: str) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_KEYS:
        if payload.get(key) is None:
            errors.append(f"missing required key: {key}")

    emotion = payload.get("emotion")
    if emotion is not None and (not isinstance(emotion, str) or not re.fullmatch(r"[a-z0-9_]+", emotion)):
        errors.append("emotion must be a short lowercase English label")

    action = payload.get("action")
    if action is not None and (not isinstance(action, str) or not re.fullmatch(r"[a-z0-9_]+", action)):
        errors.append("action must be a short lowercase English label")

    shares_news = payload.get("shares_news")
    if shares_news is not None and not isinstance(shares_news, bool):
        errors.append("shares_news must be a boolean")

    influences_count = payload.get("influences_count")
    if influences_count is not None:
        if not isinstance(influences_count, int) or isinstance(influences_count, bool):
            errors.append("influences_count must be an integer")
        else:
            if influences_count < 0:
                errors.append("influences_count must be >= 0")

            influence_radius = profile.get("influence_radius")
            if isinstance(influence_radius, int) and influences_count > influence_radius:
                errors.append("influences_count exceeds influence_radius")

    post_content = payload.get("post_content")
    if post_content is not None:
        if not isinstance(post_content, str) or not post_content.strip():
            errors.append("post_content must be a non-empty Bangla string")
        else:
            if not re.search(r"[\u0980-\u09FF]", post_content):
                errors.append("post_content must contain Bangla characters")
            if "???" in post_content or "�" in post_content:
                errors.append("post_content contains placeholder or encoding noise")
            if re.search(r"[A-Za-z]{3,}", post_content):
                errors.append("post_content should not contain English words")

            if scenario_targets_rice(scenario):
                if "চাল" not in post_content:
                    errors.append("post_content must mention চাল for a rice scenario")

                lowered = post_content.lower()
                for term in FORBIDDEN_COMMODITY_TERMS:
                    if term in post_content or term in lowered:
                        errors.append(f"post_content mentions forbidden commodity term: {term}")
                        break

    return errors


def repair_payload(
    client: OpenAI,
    model: str,
    profile: dict[str, Any],
    scenario: str,
    invalid_content: str,
    validation_errors: list[str],
) -> dict[str, Any]:
    system_prompt = (
        "You repair invalid OPS simulation JSON.\n"
        "Return exactly one valid JSON object with exactly these keys: "
        "emotion, action, shares_news, influences_count, post_content.\n"
        "Do not add any extra keys.\n"
        "Do not change the person, city, job, or scenario.\n"
        "If the scenario is about rice, the Bangla text must mention only চাল and no other commodity.\n"
        "Write simple, clean Bangla. No code fences."
    )

    if not scenario_targets_rice(scenario):
        output_template = (
            "{\"emotion\":\"concerned\",\"action\":\"watch_closely\",\"shares_news\":false,"
            "\"influences_count\":6,\"post_content\":\"ঘোষণাটা আগে সত্যি কীভাবে কার্যকর হয় তা দেখে নিতে হবে। এখনই বেশি ভরসা করা ঠিক হবে না।\"}"
        )

    user_prompt = (
        "Persona:\n"
        f"{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n"
        "Scenario:\n"
        f"{scenario}\n\n"
        "Invalid output to repair:\n"
        f"{invalid_content}\n\n"
        "Validation errors:\n"
        f"{json.dumps(validation_errors, ensure_ascii=False, indent=2)}\n\n"
        "Repair rules:\n"
        "- Keep the output faithful to Rahim.\n"
        "- emotion and action must be short lowercase English labels.\n"
        "- shares_news must be true or false.\n"
        "- influences_count must be an integer and not exceed influence_radius.\n"
        "- post_content must be natural Bangla, short, clear, and about rice only.\n"
        "- Return JSON only."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    repaired_content = response.choices[0].message.content
    return normalize_payload(extract_json_payload(repaired_content))


def _trust_bucket(profile: dict[str, Any]) -> str:
    trust_government = profile.get("current_trust_government", profile.get("trust_government"))
    if not isinstance(trust_government, int):
        return "medium"
    if trust_government <= 3:
        return "low"
    if trust_government >= 7:
        return "high"
    return "medium"


def _fear_phrase(profile: dict[str, Any]) -> str:
    primary_fear = str(profile.get("primary_fear") or "").strip().lower()
    if "son" in primary_fear and "education" in primary_fear:
        return "ছেলের পড়াশোনার খরচ"
    if "education" in primary_fear:
        return "পড়াশোনার খরচ"
    if "job" in primary_fear or "income" in primary_fear:
        return "রোজগারের চাপ"
    return "সংসারের খরচ"


def _rice_fallback_post_content(profile: dict[str, Any], shares_news: bool) -> str:
    trust_bucket = _trust_bucket(profile)
    fear_phrase = _fear_phrase(profile)

    if shares_news:
        if trust_bucket == "low":
            return (
                f"আগামী মাসে চালের দাম ৪০% বাড়লে আমাদের মতো দৈনিক আয়ের মানুষের খুব কষ্ট হবে। "
                f"{fear_phrase} কীভাবে সামলাব, তাই সবাই এখন থেকেই হিসাব করে চলেন।"
            )
        if trust_bucket == "high":
            return (
                f"চালের দাম ৪০% বাড়ার খবরটা সত্যি হলে সংসারের ওপর চাপ বাড়বে। "
                f"আগে থেকেই খরচ সামলে চলা ভালো, না হলে {fear_phrase} টান পড়বে।"
            )
        return (
            f"চালের দাম ৪০% বাড়লে সংসার চালানো কঠিন হবে। "
            f"{fear_phrase} সামলাতে এখন থেকেই একটু সাবধানে চলা দরকার।"
        )

    if trust_bucket == "low":
        return (
            f"চালের দাম ৪০% বাড়লে সংসার চালানো খুব কঠিন হয়ে যাবে। "
            f"{fear_phrase} কীভাবে দেব, সেই চিন্তায় আছি।"
        )
    if trust_bucket == "high":
        return (
            f"চালের দাম ৪০% বাড়লে খরচ বাড়বে, তাই আগে থেকেই হিসাব করে চলতে হবে। "
            f"{fear_phrase} যেন বন্ধ না হয়, সেটাই এখন ভাবছি।"
        )
    return (
        f"চালের দাম ৪০% বাড়লে আমাদের খরচ অনেক চাপবে। "
        f"{fear_phrase} কীভাবে সামলাব, তা নিয়েই চিন্তা করছি।"
    )


def deterministic_local_fix(
    payload: dict[str, Any],
    profile: dict[str, Any],
    scenario: str,
) -> dict[str, Any]:
    fixed = normalize_payload(payload)

    influence_radius = profile.get("influence_radius")
    if not isinstance(influence_radius, int) or influence_radius < 0:
        influence_radius = 0

    shares_news = fixed.get("shares_news")
    if not isinstance(shares_news, bool):
        shares_news = bool(profile.get("fb_intensity", 0) >= 5)
    fixed["shares_news"] = shares_news

    emotion = fixed.get("emotion")
    if not isinstance(emotion, str) or not re.fullmatch(r"[a-z0-9_]+", emotion):
        if scenario_targets_rice(scenario):
            emotion = "worried" if _trust_bucket(profile) != "low" else "anxious"
        else:
            emotion = "concerned"
    fixed["emotion"] = emotion

    action = fixed.get("action")
    if not isinstance(action, str) or not re.fullmatch(r"[a-z0-9_]+", action):
        if shares_news:
            action = "warn_neighbours" if _trust_bucket(profile) == "low" else "warn_family"
        else:
            action = "cut_spending" if _trust_bucket(profile) != "high" else "wait_and_budget"
    fixed["action"] = action

    influences_count = fixed.get("influences_count")
    if not isinstance(influences_count, int) or isinstance(influences_count, bool):
        if shares_news and influence_radius > 0:
            influences_count = max(1, min(influence_radius, max(5, influence_radius // 3)))
        else:
            influences_count = 0
    influences_count = max(0, min(influences_count, influence_radius))
    fixed["influences_count"] = influences_count

    if scenario_targets_rice(scenario):
        post_content = _rice_fallback_post_content(profile, shares_news)
    else:
        fear = profile.get("primary_fear") or "পরিবারের ভবিষ্যৎ"
        post_content = (
            f"এই খবরটা আমাদের সংসারের ওপর চাপ বাড়াবে। {fear} নিয়েই এখন সবচেয়ে বেশি চিন্তা হচ্ছে।"
        )

    fixed["post_content"] = post_content
    return fixed


def generate_validated_payload(
    client: OpenAI,
    model: str,
    profile: dict[str, Any],
    scenario: str,
    temperature: float,
    memory_context: Optional[str] = None,
) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        messages=build_messages_dynamic(profile, scenario, memory_context),
        response_format={"type": "json_object"},
        temperature=temperature,
    )

    raw_content = response.choices[0].message.content
    payload = normalize_payload(extract_json_payload(raw_content))
    errors = validate_payload(payload, profile, scenario)

    if not errors:
        return payload

    print(
        f"Initial output failed validation; running repair pass: {', '.join(errors)}",
        file=sys.stderr,
    )
    repaired_payload = repair_payload(
        client=client,
        model=model,
        profile=profile,
        scenario=scenario,
        invalid_content=raw_content,
        validation_errors=errors,
    )
    repaired_errors = validate_payload(repaired_payload, profile, scenario)

    if repaired_errors:
        print(
            "Repair output still failed validation; applying deterministic local fix: "
            + ", ".join(repaired_errors),
            file=sys.stderr,
        )
        final_payload = deterministic_local_fix(repaired_payload, profile, scenario)
        final_errors = validate_payload(final_payload, profile, scenario)
        if final_errors:
            raise ValueError(
                "Output validation failed after deterministic local fix: "
                + "; ".join(final_errors)
            )
        return final_payload

    return repaired_payload


def extract_state_signals(
    client: OpenAI,
    model: str,
    profile: dict[str, Any],
    scenario: str,
    visible_result: dict[str, Any],
) -> dict[str, Any]:
    """Run the internal signal-extraction pass used for temporal continuity."""
    system_prompt = (
        "You analyze one OPS simulation result and return JSON only.\n"
        "Return exactly two top-level keys: state_signals and outcome_note.\n"
        "state_signals must be an object with exactly these boolean keys: "
        + ", ".join(STATE_SIGNAL_KEYS)
        + ".\n"
        "Base your judgment on the scenario, persona, and visible response.\n"
        "Do not invent new facts. Use conservative inferences."
    )
    user_prompt = (
        "Persona JSON:\n"
        f"{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n"
        "Scenario:\n"
        f"{scenario}\n\n"
        "Visible simulation result:\n"
        f"{json.dumps(visible_result, ensure_ascii=False, indent=2)}\n\n"
        "Rules:\n"
        "- government_targeted: true when the scenario or response clearly targets government responsibility, policy, or institutional failure.\n"
        "- government_relief_positive: true when the scenario includes relief/subsidy/support and the agent responds in a receptive or reassured way.\n"
        "- fear_triggered: true when the agent's primary fear is clearly activated.\n"
        "- positive_outcome: true when the response indicates reassurance, relief, or reduced pressure.\n"
        "- public_exposure: true when the agent publicly posted/shared in a socially risky or visible way.\n"
        "- outcome_note: one short sentence in English.\n"
        "JSON only."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    content = response.choices[0].message.content
    parsed = extract_json_payload(content)
    raw_signals = parsed.get("state_signals") or {}
    normalized_signals = {key: bool(raw_signals.get(key, False)) for key in STATE_SIGNAL_KEYS}
    return {
        "state_signals": normalized_signals,
        "outcome_note": str(parsed.get("outcome_note", "") or "").strip(),
    }


def heuristic_state_signals(
    profile: dict[str, Any],
    scenario: str,
    visible_result: dict[str, Any],
) -> dict[str, Any]:
    """Fallback signal extraction if the LLM signal pass fails."""
    scenario_lower = scenario.lower()
    emotion = str(visible_result.get("emotion", "") or "").lower()
    action = str(visible_result.get("action", "") or "").lower()
    post_content = str(visible_result.get("post_content", "") or "")
    shares_news = bool(visible_result.get("shares_news"))
    trust_low = (_trust_bucket(profile) == "low")
    primary_fear = str(profile.get("primary_fear", "") or "").lower()

    government_keywords = ("government", "govt", "minister", "subsidy", "relief", "policy")
    government_related = any(keyword in scenario_lower for keyword in government_keywords)
    relief_related = any(keyword in scenario_lower for keyword in ("relief", "subsidy", "support"))
    fear_triggered = any(term and term in scenario_lower for term in primary_fear.split()) or emotion in {"worried", "anxious", "angry", "panic", "desperate"}
    positive_outcome = relief_related and (emotion in {"calm", "hopeful"} or action == "wait_and_budget")

    return {
        "state_signals": {
            "government_targeted": government_related and (trust_low or emotion in {"angry", "betrayed"}),
            "government_relief_positive": relief_related and positive_outcome,
            "fear_triggered": fear_triggered,
            "positive_outcome": positive_outcome,
            "public_exposure": shares_news or bool(post_content.strip()),
        },
        "outcome_note": "Generated from heuristic OPS continuity rules.",
    }


def build_messages(profile: dict, scenario: str, memory_context: Optional[str] = None) -> list[dict]:
    persona_schema = {
        "name": profile.get("name"),
        "age": profile.get("age"),
        "profession": profile.get("profession"),
        "country": profile.get("country"),
        "bio": profile.get("bio"),
        "persona": profile.get("persona"),
        "trust_government": profile.get("current_trust_government", profile.get("trust_government")),
        "shame_sensitivity": profile.get("current_shame_sensitivity", profile.get("shame_sensitivity")),
        "primary_fear": profile.get("primary_fear"),
        "influence_radius": profile.get("influence_radius"),
        "fb_intensity": profile.get("fb_intensity"),
        "dialect": profile.get("dialect"),
        "income_stability": profile.get("income_stability"),
        "rumour_amplifier": profile.get("rumour_amplifier"),
        "baseline_anxiety": profile.get("baseline_anxiety"),
        "cumulative_stress": profile.get("cumulative_stress"),
    }

    system_prompt = (
        "You simulate exactly one OPS agent and must stay faithful to the supplied persona and scenario.\n"
        "Return exactly one valid JSON object with exactly these keys: "
        "emotion, action, shares_news, influences_count, post_content.\n"
        "Hard rules:\n"
        "1. Do not change the topic, commodity, city, job, or fear from the input.\n"
        "2. If the scenario is about rice, mention only rice / চাল. Never mention sugar, oil, wheat, or any other commodity.\n"
        "3. emotion and action must be short lowercase English labels.\n"
        "4. shares_news must be true or false.\n"
        "5. influences_count must be an integer and must not exceed the supplied influence_radius.\n"
        "6. post_content must be natural colloquial Bangla in 1-2 short sentences.\n"
        "7. post_content must not contain English words except unavoidable names.\n"
        "8. No markdown, no code fences, no explanations, no extra keys.\n"
        "9. If the persona says rumour_amplifier=false and the news source is reliable, keep the tone cautious and non-exaggerated.\n"
        "10. If unsure, produce simpler Bangla, not more creative Bangla."
    )
    if memory_context:
        system_prompt += f"\n\nAgent history:\n{memory_context}"
    user_prompt = (
        "Simulate Rahim only.\n\n"
        "Agent persona JSON:\n"
        f"{json.dumps(persona_schema, ensure_ascii=False, indent=2)}\n\n"
        "Scenario:\n"
        f"{scenario}\n\n"
        "Use these persona anchors:\n"
        "- He is a 42-year-old CNG driver in Sylhet on daily wages.\n"
        "- trust_government is low, so he does not sound trusting toward official reassurances.\n"
        "- shame_sensitivity is high, so he worries about social embarrassment and family failure.\n"
        "- primary_fear is his son's education.\n"
        "- rumour_amplifier is false, so he should not invent or amplify beyond the given scenario.\n"
        "- fb_intensity is high enough that he may post or share, but his tone should stay grounded.\n\n"
        "Output template:\n"
        "{\"emotion\":\"worried\",\"action\":\"warn_family\",\"shares_news\":true,\"influences_count\":12,"
        "\"post_content\":\"চালের দাম এভাবে বাড়লে আমাদের মতো দৈনিক আয়ের মানুষের খুব কষ্ট হবে। ছেলের পড়াশোনার খরচ কীভাবে সামলাব, সেই চিন্তায় আছি।\"}\n\n"
        "Final reminders:\n"
        "- Keep the scenario focused on rice only.\n"
        "- Make the Bangla plain, readable, and clean.\n"
        "- JSON only."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_messages_dynamic(profile: dict, scenario: str, memory_context: Optional[str] = None) -> list[dict]:
    """Scenario-aware replacement for the older single-scenario prompt builder."""
    trust_government = profile.get("current_trust_government", profile.get("trust_government"))
    shame_sensitivity = profile.get("current_shame_sensitivity", profile.get("shame_sensitivity"))
    persona_schema = {
        "name": profile.get("name"),
        "age": profile.get("age"),
        "profession": profile.get("profession"),
        "country": profile.get("country"),
        "bio": profile.get("bio"),
        "persona": profile.get("persona"),
        "trust_government": trust_government,
        "shame_sensitivity": shame_sensitivity,
        "primary_fear": profile.get("primary_fear"),
        "influence_radius": profile.get("influence_radius"),
        "fb_intensity": profile.get("fb_intensity"),
        "dialect": profile.get("dialect"),
        "income_stability": profile.get("income_stability"),
        "rumour_amplifier": profile.get("rumour_amplifier"),
        "baseline_anxiety": profile.get("baseline_anxiety"),
        "cumulative_stress": profile.get("cumulative_stress"),
    }

    system_prompt = (
        "You simulate exactly one OPS agent and must stay faithful to the supplied persona and scenario.\n"
        "Return exactly one valid JSON object with exactly these keys: emotion, action, shares_news, influences_count, post_content.\n"
        "Hard rules:\n"
        "1. Do not change the topic, commodity, city, job, or fear from the input.\n"
        "2. If the scenario is about rice, mention only rice / চাল. Never mention sugar, oil, wheat, or any other commodity.\n"
        "3. emotion and action must be short lowercase English labels.\n"
        "4. shares_news must be true or false.\n"
        "5. influences_count must be an integer and must not exceed the supplied influence_radius.\n"
        "6. post_content must be natural colloquial Bangla in 1-2 short sentences.\n"
        "7. post_content must not contain English words except unavoidable names.\n"
        "8. No markdown, no code fences, no explanations, no extra keys.\n"
        "9. If the persona says rumour_amplifier=false and the news source is reliable, keep the tone cautious and non-exaggerated.\n"
        "10. If unsure, produce simpler Bangla, not more creative Bangla."
    )
    if memory_context:
        system_prompt += f"\n\nAgent history:\n{memory_context}"

    name = profile.get("name") or "the supplied agent"
    age = profile.get("age") or "unknown"
    profession = profile.get("profession") or "unknown profession"
    country = profile.get("country") or "South Asia"
    primary_fear = profile.get("primary_fear") or "family security"
    dialect = profile.get("dialect") or "their usual social-media style"
    income_stability = profile.get("income_stability") or "unclear"
    rumour_amplifier = profile.get("rumour_amplifier")
    trust_note = "low" if isinstance(trust_government, int) and trust_government <= 3 else "moderate/high"
    shame_note = "high" if isinstance(shame_sensitivity, int) and shame_sensitivity >= 7 else "low/moderate"

    if scenario_targets_rice(scenario):
        output_template = (
            "{\"emotion\":\"worried\",\"action\":\"warn_family\",\"shares_news\":true,"
            "\"influences_count\":12,\"post_content\":\"চালের দাম এভাবে বাড়লে আমাদের মতো দৈনিক আয়ের মানুষের খুব কষ্ট হবে। ছেলের পড়াশোনার খরচ কীভাবে সামলাব, সেই চিন্তায় আছি।\"}"
        )
    else:
        output_template = (
            "{\"emotion\":\"hopeful\",\"action\":\"wait_and_budget\",\"shares_news\":false,"
            "\"influences_count\":6,\"post_content\":\"সরকারি সহায়তা সত্যি হলে কিছুটা ভরসা পাওয়া যাবে। তবু সংসারের হিসাব খুব সাবধানে করতে হবে।\"}"
        )

    user_prompt = (
        f"Simulate {name} only.\n\n"
        "Agent persona JSON:\n"
        f"{json.dumps(persona_schema, ensure_ascii=False, indent=2)}\n\n"
        "Scenario:\n"
        f"{scenario}\n\n"
        "Use these persona anchors:\n"
        f"- They are {age} years old, work as {profession}, and are based in or tied to {country}.\n"
        f"- trust_government is {trust_note}, so the response should reflect that current level of institutional trust.\n"
        f"- shame_sensitivity is {shame_note}, so public embarrassment and family reputation should matter accordingly.\n"
        f"- primary_fear is {primary_fear}.\n"
        f"- income stability is {income_stability}, and dialect/style is {dialect}.\n"
        f"- rumour_amplifier is {rumour_amplifier}, so willingness to relay uncertain news should stay consistent.\n"
        "- fb_intensity indicates whether the agent is likely to post or stay quiet, but the tone should stay grounded.\n\n"
        "Output template:\n"
        f"{output_template}\n\n"
        "Final reminders:\n"
        "- Keep the output tightly aligned to the exact scenario text.\n"
        "- Make the Bangla plain, readable, and clean.\n"
        "- JSON only."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single-agent OPS probe against the local LLM.")
    parser.add_argument("--profile", required=True, help="Path to a profile JSON file.")
    parser.add_argument("--scenario", required=True, help="Scenario text to simulate.")
    parser.add_argument("--project-id", default="ops_probe", help="Project scope used for temporal continuity persistence.")
    parser.add_argument("--model", default=None, help="Override model name.")
    parser.add_argument("--base-url", default=None, help="Override OpenAI-compatible base URL.")
    parser.add_argument("--api-key", default=None, help="Override API key.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    args = parser.parse_args()

    load_dotenv(project_root / ".env", override=True)

    profile = load_profile(Path(args.profile))
    restored_state = None
    try:
        restored_state = asyncio.run(load_agent_state(profile.user_id, args.project_id))
    except Exception as exc:
        print(f"Failed to load persisted state: {exc}", file=sys.stderr)
    if restored_state:
        profile.simulation_history = list(restored_state.get("simulation_history") or [])
        profile.baseline_anxiety = float(restored_state.get("baseline_anxiety", profile.baseline_anxiety) or profile.baseline_anxiety)
        if restored_state.get("current_trust_government") is not None:
            profile.current_trust_government = int(restored_state["current_trust_government"])
        if restored_state.get("current_shame_sensitivity") is not None:
            profile.current_shame_sensitivity = int(restored_state["current_shame_sensitivity"])
        profile.cumulative_stress = float(restored_state.get("cumulative_stress", profile.cumulative_stress) or profile.cumulative_stress)
        profile.last_simulation_date = restored_state.get("last_simulation_date") or profile.last_simulation_date

    profile_dict = profile.to_dict()
    memory_context = profile.build_memory_context() if profile.simulation_history else ""
    model = args.model or os.environ.get("LLM_MODEL_NAME", "qwen2.5:7b")
    base_url = args.base_url or os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    api_key = args.api_key or os.environ.get("LLM_API_KEY", "ollama")

    client = OpenAI(api_key=api_key, base_url=base_url)
    payload = generate_validated_payload(
        client=client,
        model=model,
        profile=profile_dict,
        scenario=args.scenario,
        temperature=args.temperature,
        memory_context=memory_context,
    )

    try:
        signal_data = extract_state_signals(
            client=client,
            model=model,
            profile=profile_dict,
            scenario=args.scenario,
            visible_result=payload,
        )
    except Exception as exc:
        print(f"Signal extraction failed; falling back to heuristic continuity signals: {exc}", file=sys.stderr)
        signal_data = heuristic_state_signals(profile_dict, args.scenario, payload)

    canonical_result = dict(payload)
    canonical_result.update(signal_data)
    state_change = profile.apply_simulation_outcome(
        simulation_id=f"probe_{Path(args.profile).stem}_{int(time.time())}",
        scenario=args.scenario,
        result=canonical_result,
    )

    try:
        asyncio.run(save_agent_state(profile, args.project_id))
    except Exception as exc:
        print(f"Failed to save persisted state: {exc}", file=sys.stderr)

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps({"state_change": state_change}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
