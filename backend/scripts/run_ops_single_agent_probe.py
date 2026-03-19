import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


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


def load_profile(profile_path: Path) -> dict:
    with profile_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        if not data:
            raise ValueError(f"No profiles found in {profile_path}")
        return data[0]

    return data


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
    trust_government = profile.get("trust_government")
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
) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        messages=build_messages(profile, scenario),
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


def build_messages(profile: dict, scenario: str) -> list[dict]:
    persona_schema = {
        "name": profile.get("name"),
        "age": profile.get("age"),
        "profession": profile.get("profession"),
        "country": profile.get("country"),
        "bio": profile.get("bio"),
        "persona": profile.get("persona"),
        "trust_government": profile.get("trust_government"),
        "shame_sensitivity": profile.get("shame_sensitivity"),
        "primary_fear": profile.get("primary_fear"),
        "influence_radius": profile.get("influence_radius"),
        "fb_intensity": profile.get("fb_intensity"),
        "dialect": profile.get("dialect"),
        "income_stability": profile.get("income_stability"),
        "rumour_amplifier": profile.get("rumour_amplifier"),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single-agent OPS probe against the local LLM.")
    parser.add_argument("--profile", required=True, help="Path to a profile JSON file.")
    parser.add_argument("--scenario", required=True, help="Scenario text to simulate.")
    parser.add_argument("--model", default=None, help="Override model name.")
    parser.add_argument("--base-url", default=None, help="Override OpenAI-compatible base URL.")
    parser.add_argument("--api-key", default=None, help="Override API key.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env", override=True)

    profile = load_profile(Path(args.profile))
    model = args.model or os.environ.get("LLM_MODEL_NAME", "qwen2.5:7b")
    base_url = args.base_url or os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    api_key = args.api_key or os.environ.get("LLM_API_KEY", "ollama")

    client = OpenAI(api_key=api_key, base_url=base_url)
    payload = generate_validated_payload(
        client=client,
        model=model,
        profile=profile,
        scenario=args.scenario,
        temperature=args.temperature,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
