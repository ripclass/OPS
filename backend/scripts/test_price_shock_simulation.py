"""
OPS Multi-Country Price Shock Simulation
=========================================
Scenario: Rice +40%, Wheat +35% across South Asia. El Nino + India export ban.
No government relief announced.

750 agents across 5 countries. Rule-based profile generation (no LLM needed).
Behavioral cascade analysis from occupational reality data.
"""

import json
import os
import sys
import random
import shutil
import tempfile
import types
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from unittest.mock import patch, MagicMock

# --- Stub heavy imports ---
backend_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, backend_dir)

class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return type(name, (), {"__init__": lambda self, *a, **kw: None})

_STUB_PREFIXES = ["zep_cloud", "camel", "supabase", "fitz", "readability", "bs4", "lxml"]

class _StubImportHook:
    def find_module(self, fullname, path=None):
        for prefix in _STUB_PREFIXES:
            if fullname == prefix or fullname.startswith(prefix + "."):
                return self
        return None
    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = _StubModule(fullname)
        mod.__path__ = []
        mod.__loader__ = self
        sys.modules[fullname] = mod
        return mod

_hook = _StubImportHook()
sys.meta_path.insert(0, _hook)
for mod_name in ["zep_cloud", "zep_cloud.client", "zep_cloud.types", "camel", "camel.oasis",
                  "supabase", "fitz", "readability", "readability.readability", "bs4", "lxml", "lxml.html"]:
    _hook.load_module(mod_name)

from app.services.ops_population_generator import (
    OPSPopulationGenerator, normalize_ops_population_params,
    BANGLADESH_OCCUPATIONAL_REALITY, INDIA_OCCUPATIONAL_REALITY,
    PAKISTAN_OCCUPATIONAL_REALITY, SRI_LANKA_OCCUPATIONAL_REALITY,
    NEPAL_OCCUPATIONAL_REALITY,
)
from app.services.oasis_profile_generator import OasisAgentProfile


# =============================================================================
# SCENARIO DEFINITION
# =============================================================================

SCENARIO = {
    "title": "South Asia Rice-Wheat Price Shock",
    "trigger": "Rice +40%, Wheat +35% — El Nino crop failure + India export ban",
    "relief": "No immediate government relief announced",
    "context": (
        "Global commodity markets spike. Rice prices increase 40% and wheat prices "
        "increase 35% across South Asia simultaneously. The increase is driven by "
        "El Nino crop failures in Southeast Asia combined with export restrictions "
        "from India. The price shock hits all five countries within the same week. "
        "Local governments announce the price increase has no immediate relief plan."
    ),
}

COUNTRY_CONFIGS = {
    "Bangladesh": {
        "n_agents": 200,
        "segments": {
            "rural": 50,
            "urban_working": 80,
            "middle_class": 40,
            "students": 30,
        },
        "region": "mixed",
    },
    "India": {
        "n_agents": 200,
        "segments": {
            "rural": 60,       # UP/Bihar rural
            "urban_working": 60,  # Delhi urban working
            "corporate": 40,     # South India urban (mapped to corporate for IT workers)
            "middle_class": 40,
        },
        "region": "mixed",
    },
    "Pakistan": {
        "n_agents": 150,
        "segments": {
            "urban_working": 50,  # Punjab urban
            "urban_working": 50,  # Karachi (combined into urban_working)
            "rural": 30,          # Rural Sindh
            "women": 20,          # KP (mapped to women for restricted access)
        },
        "region": "mixed",
    },
    "Sri Lanka": {
        "n_agents": 100,
        "segments": {
            "urban_working": 30,   # Sinhala working class
            "rural": 20,           # Plantation Tamil
            "migration_workers": 20, # Jaffna Tamil (war-affected, migration-linked)
            "middle_class": 15,    # Muslim + Colombo middle
            "students": 15,        # Mixed
        },
        "region": "mixed",
    },
    "Nepal": {
        "n_agents": 100,
        "segments": {
            "rural": 40,           # Hill remittance households
            "urban_working": 30,   # Kathmandu urban
            "women": 30,           # Terai Madhesi
        },
        "region": "mixed",
    },
}


# =============================================================================
# BEHAVIORAL MODEL
# =============================================================================

@dataclass
class AgentBehavior:
    """Predicted behavioral response to the price shock."""
    agent_id: int
    name: str
    country: str
    segment: str
    occupation: str
    location: str
    dialect: str
    primary_fear: str
    trust_government: int
    shame_sensitivity: int
    fb_intensity: int
    baseline_anxiety: float
    # Computed behaviors
    dominant_emotion: str = ""
    share_probability: float = 0.0
    is_amplifier: bool = False
    cascade_reach: int = 0
    post_content: str = ""
    action_taken: str = ""


def compute_behavior(profile: OasisAgentProfile, country: str) -> AgentBehavior:
    """Compute predicted behavioral response to food price shock."""
    behavior = AgentBehavior(
        agent_id=profile.user_id,
        name=profile.name,
        country=country,
        segment=profile.source_entity_type or "unknown",
        occupation=profile.profession or "unknown",
        location=profile.location or "unknown",
        dialect=profile.dialect or "standard",
        primary_fear=profile.primary_fear or "price increase",
        trust_government=profile.trust_government or 5,
        shame_sensitivity=profile.shame_sensitivity or 5,
        fb_intensity=profile.fb_intensity or 5,
        baseline_anxiety=profile.baseline_anxiety or 5.0,
    )

    segment = behavior.segment
    trust = behavior.trust_government
    fb = behavior.fb_intensity
    anxiety = behavior.baseline_anxiety

    # --- Dominant Emotion ---
    if segment in ("rural", "women"):
        if anxiety > 7:
            behavior.dominant_emotion = "panic"
        elif trust < 3:
            behavior.dominant_emotion = "rage"
        else:
            behavior.dominant_emotion = "fear"
    elif segment == "urban_working":
        if trust < 3:
            behavior.dominant_emotion = "rage"
        elif anxiety > 6:
            behavior.dominant_emotion = "panic"
        else:
            behavior.dominant_emotion = "frustration"
    elif segment == "students":
        if trust < 3:
            behavior.dominant_emotion = "rage"
        else:
            behavior.dominant_emotion = "outrage"
    elif segment == "middle_class":
        if anxiety > 7:
            behavior.dominant_emotion = "anxiety"
        else:
            behavior.dominant_emotion = "frustration"
    elif segment in ("corporate", "migration_workers"):
        behavior.dominant_emotion = "concern"
    else:
        behavior.dominant_emotion = "worry"

    # --- Share Probability (0-1) ---
    base_share = min(fb / 10.0, 1.0)
    if trust < 3:
        base_share *= 1.4  # Low trust = more sharing (distrust drives info-seeking)
    if segment == "students":
        base_share *= 1.3  # Students amplify
    if anxiety > 7:
        base_share *= 1.2
    behavior.share_probability = min(base_share, 1.0)

    # --- Amplifier Node ---
    behavior.is_amplifier = (
        fb >= 7 and trust <= 4 and
        segment in ("students", "urban_working", "women") and
        behavior.share_probability > 0.6
    )

    # --- Cascade Reach ---
    influence = profile.influence_radius or 50
    if behavior.is_amplifier:
        behavior.cascade_reach = int(influence * 2.5)
    elif behavior.share_probability > 0.5:
        behavior.cascade_reach = int(influence * 1.5)
    else:
        behavior.cascade_reach = influence

    # --- Action Taken ---
    if behavior.dominant_emotion == "panic":
        behavior.action_taken = "panic_buying"
    elif behavior.dominant_emotion == "rage":
        behavior.action_taken = "protest_call"
    elif behavior.dominant_emotion == "outrage":
        behavior.action_taken = "viral_post"
    elif behavior.dominant_emotion in ("frustration", "anxiety"):
        behavior.action_taken = "budget_cutting"
    elif behavior.dominant_emotion == "concern":
        behavior.action_taken = "wait_and_watch"
    else:
        behavior.action_taken = "silent_coping"

    # --- Generate Post Content in Native Dialect ---
    behavior.post_content = generate_native_post(behavior, country)

    return behavior


def generate_native_post(b: AgentBehavior, country: str) -> str:
    """Generate a representative social media post in the agent's native dialect/language."""

    templates = {
        "Bangladesh": {
            "rural": {
                "fear": "Chaaler daam eto beshii, ebar ki hobe amader? Sorkarer dike takaiya achi kintu keu kichhu bolchhe na.",
                "panic": "40% daam barrchhe!! Bazaar e giye dekhi sob shesh. Ebar poriba ki diye ranna korbo?? #ChaalerDaam",
                "rage": "Eid er aagei chaal 40% barrlo! Shorkarer kono plan nai! Gariber jibon niye politics! #DaamBadchhe",
            },
            "urban_working": {
                "frustration": "Garments er motan e toh bodhlai nai, kintu bazarer daam dwidgun. Rickshaw er bhara bariye dilam kintu keu dibe na. Ranna korbo ki diye?",
                "rage": "Chaal kinlam 80 taka kg — shesh mash e bhat khete parbo na. Shorkarer onek kotha, kaj ki? #RicePrice",
                "panic": "Pathao commission kaatle dilam, upore chaal 40% barrchhe! Biye-bacchader bhaat debo ki?? Polapain starving!",
            },
            "middle_class": {
                "anxiety": "I calculated our monthly grocery bill just went up by BDT 3,000+. With school fees and coaching costs, we are drowning. Middle class means invisible to government.",
                "frustration": "Rice 40% up, wheat 35% up. My salary? 0% up. This isn't a crisis — this is systematic elimination of the middle class. #MiddleClassCrisis",
            },
            "students": {
                "outrage": "Rice er daam 40% barrlo ar sorkarer 'plan nai'?? July te amra ke shesh korlam — eder e shesh korbo naki?? #PriceHike #StudentPower",
                "rage": "Amar baba rickshaw chalan, amake coaching er taka dite pare na already. Ebar chaaler daam?? How are we supposed to survive AND study??",
            },
        },
        "India": {
            "rural": {
                "fear": "Chawal ka daam 40% badh gaya. Hum kisan hain lekin bazaar mein hamara mahine ka budget khatam ho gaya. Sarkar kab sunega?",
                "panic": "Atta 35% mehnga! Gheee ka daam already double! Bacchon ko kya khilayein?? #MehangiDar #KisanKiHaalat",
                "rage": "Modi ji ne export ban laga diya lekin hamare gaon mein daam badhte jaa rahe. Ye kya mazaak hai? #PriceHike",
            },
            "urban_working": {
                "frustration": "Swiggy pe delivery kar kar ke Rs 500 kamata hoon. Aaj ek kg chawal Rs 55 se 77. Ek din ki kamaai mein khaana bhi nahi milega. #GigWorkerLife",
                "rage": "Auto ka CNG badha, chawal badha, atta badha — mera kiraya wahi. Customer ko batao toh gussa karte. Sab ke upar price badhta hai bus mazdoor ke wages nahi. #MehangiDar",
            },
            "corporate": {
                "concern": "Food inflation 40% is not just a rural problem. Urban India spends 30%+ of income on food. This will hit consumption, FMCG stocks, and Q3 earnings. Brace for impact.",
            },
            "middle_class": {
                "anxiety": "Monthly grocery: Rs 8,000 → Rs 11,500. EMI + school fees + now THIS. The Indian middle class is a shock absorber with no suspension left.",
                "frustration": "Government banned rice exports to control domestic prices but prices went UP. Classic. We pay taxes, we get nothing. #MiddleClassMatters",
            },
        },
        "Pakistan": {
            "rural": {
                "fear": "Aata 35% mehnga ho gaya. Bijli ka bill pehle se do guna. Ab roti bhi afford nahi hogi. Allah reham kare.",
                "panic": "Gehun ka aata Rs 180/kg se zyada!! Eid ke baad kya hoga?? Bachche bhooke so rahe hain already! #MehangiDar",
            },
            "urban_working": {
                "rage": "Chawal 40% badha, aata 35%, bijli double, gas gayab. Imran Khan jail mein, mulk tabah. Ye azaadi hai ya ghulami?? #PriceHike",
                "frustration": "Careem se daily 1500 kamata tha ab petrol ke baad 800 bachta hai. Upar se aate ka bhav... family ko kaise feed karoon? #KarachiProblems",
            },
            "women": {
                "fear": "Gas cylinder khatam. Aata ka daam asman pe. Bachche school se aaye toh roti nahi thi. Ye haal hai Pakistan ka. Koi sunega?",
            },
        },
        "Sri Lanka": {
            "urban_working": {
                "frustration": "Rice Rs 250/kg now?? 2022 la wage eka wage thamai gahanna bari. Government promises recovery but my salary still below 2019 level. Mata baya #PriceHike",
                "panic": "FTZ eke kamkaruwanta haal wenna iddi — Trump tariff one eka one langa, dan hal ganan eka!! #GarmentWorkers",
            },
            "rural": {
                "fear": "Wage Rs 1,350 per day, rice Rs 250/kg. Estate line room la 5 people feed karanum. How?? Plantation company profit ekak pennanne nathuwa!",
            },
            "migration_workers": {
                "fear": "Arisi vilai 40% yeridhuchu! Naan Jaffna la irundhu varein. Poda 2009 la porandha — ippo verum food crisis. Endha government um trust panna mudiyaadhu.",
            },
            "middle_class": {
                "anxiety": "2022 crisis wiped my savings. Now rice +40%? I can't go through this again. Half my friends are in Australia already. Should I leave too? #SriLankaCrisis",
            },
        },
        "Nepal": {
            "rural": {
                "fear": "Chamal ko bhau 40% badhyo! Shreeman Qatar ma chan, paisa pathaucha tara aba pugdaina. Bachha haru lai ke khuwaaune? #DaamBadhyo",
                "panic": "Gahu 35% mahango! IME bata aako paisa 2 hapta pani tikdaina aba. Desh ma kei chaina — sabai baahira gayera ke faaida?",
            },
            "urban_working": {
                "frustration": "Pathao chalayera din ko 1500 kamaauchhu. Chamal ko daam herda — ek din ko kamaai le 2 kg chamal matra kinchha. Balen dai le yo hernu paryo! #KathmanduLife",
                "rage": "September ma hami le aandolan garera Oli lai hataayaum — tara daam ta jhannai badhyo! Naya sarkar le pani kei garena?? #PriceHike #RSP",
            },
            "women": {
                "fear": "Bhat ko daam 40% badhyo. Budhale Qatar bata paisa pathauchhan tara mahina ko Rs 30,000 le aba kei hudaina. Chhora ko school fees, sasuma ko ausadhi — kasari manage garne? #LeftBehind",
            },
        },
    }

    country_t = templates.get(country, {})
    segment_t = country_t.get(b.segment, country_t.get("rural", {}))
    emotion = b.dominant_emotion

    # Map emotion to template key
    emotion_key = emotion
    if emotion in ("outrage", "rage"):
        emotion_key = "rage"
    elif emotion in ("panic",):
        emotion_key = "panic"
    elif emotion in ("anxiety", "frustration"):
        emotion_key = random.choice(["frustration", "anxiety"]) if "anxiety" in segment_t else "frustration"
    elif emotion in ("fear", "worry", "concern"):
        emotion_key = "fear" if "fear" in segment_t else "concern"

    post = segment_t.get(emotion_key, segment_t.get("fear", segment_t.get("frustration", f"Price shock hitting hard. {b.primary_fear}.")))

    return post


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_country_population(country: str, config: dict) -> List[AgentBehavior]:
    """Generate population and compute behaviors for one country."""

    # Build segments list with proper weighting
    segments = []
    segment_counts = config["segments"]
    for seg, count in segment_counts.items():
        segments.append(seg)

    total = sum(segment_counts.values())

    ops_params = {
        "run_type": "Domestic",
        "origin_country": country,
        "segments": segments,
        "n_agents": total,
        "region": config["region"],
    }

    normalized = normalize_ops_population_params(ops_params)
    if not normalized:
        print(f"  ERROR: Failed to normalize params for {country}")
        return []

    generator = OPSPopulationGenerator()
    profiles = generator.generate_population(
        params=normalized,
        scenario_context=SCENARIO["context"],
        use_llm=False,  # Rule-based fallback — no LLM needed
    )

    behaviors = []
    for profile in profiles:
        b = compute_behavior(profile, country)
        behaviors.append(b)

    return behaviors


def analyze_country(country: str, behaviors: List[AgentBehavior]) -> Dict[str, Any]:
    """Analyze behavioral cascade for one country."""

    emotion_counts = Counter(b.dominant_emotion for b in behaviors)
    action_counts = Counter(b.action_taken for b in behaviors)
    segment_emotions = defaultdict(lambda: Counter())
    amplifiers = [b for b in behaviors if b.is_amplifier]
    total_cascade_reach = sum(b.cascade_reach for b in behaviors)
    sharers = [b for b in behaviors if b.share_probability > 0.5]

    for b in behaviors:
        segment_emotions[b.segment][b.dominant_emotion] += 1

    # Dominant emotion per segment
    segment_dominant = {}
    for seg, counts in segment_emotions.items():
        dominant = counts.most_common(1)[0] if counts else ("unknown", 0)
        segment_dominant[seg] = {
            "emotion": dominant[0],
            "count": dominant[1],
            "total": sum(counts.values()),
            "pct": round(dominant[1] / sum(counts.values()) * 100, 1),
        }

    avg_share = sum(b.share_probability for b in behaviors) / len(behaviors)
    avg_trust = sum(b.trust_government for b in behaviors) / len(behaviors)

    return {
        "country": country,
        "total_agents": len(behaviors),
        "emotion_distribution": dict(emotion_counts.most_common()),
        "action_distribution": dict(action_counts.most_common()),
        "segment_dominant_emotion": segment_dominant,
        "amplifier_count": len(amplifiers),
        "amplifier_pct": round(len(amplifiers) / len(behaviors) * 100, 1),
        "share_rate": round(avg_share * 100, 1),
        "sharers_count": len(sharers),
        "total_cascade_reach": total_cascade_reach,
        "avg_cascade_per_agent": round(total_cascade_reach / len(behaviors)),
        "avg_trust_government": round(avg_trust, 1),
        "amplifier_nodes": [(a.name, a.segment, a.occupation, a.cascade_reach) for a in sorted(amplifiers, key=lambda x: -x.cascade_reach)[:5]],
    }


def print_sample_posts(behaviors: List[AgentBehavior], country: str, n: int = 4):
    """Print sample agent posts in native language."""
    print(f"\n  Sample Posts ({country}):")
    # Get diverse segments
    by_segment = defaultdict(list)
    for b in behaviors:
        by_segment[b.segment].append(b)

    shown = 0
    for seg, agents in by_segment.items():
        if shown >= n:
            break
        agent = random.choice(agents)
        print(f"    [{agent.segment}] {agent.name} ({agent.occupation[:40]}) — {agent.dialect}")
        print(f"    Emotion: {agent.dominant_emotion} | Action: {agent.action_taken}")
        # Wrap post content
        post = agent.post_content
        if len(post) > 120:
            print(f'    "{post[:120]}')
            print(f'     {post[120:]}"')
        else:
            print(f'    "{post}"')
        print()
        shown += 1


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("OPS MULTI-COUNTRY PRICE SHOCK SIMULATION")
    print("=" * 80)
    print(f"Scenario: {SCENARIO['title']}")
    print(f"Trigger:  {SCENARIO['trigger']}")
    print(f"Relief:   {SCENARIO['relief']}")
    print()

    all_results = {}
    all_behaviors = {}

    for country, config in COUNTRY_CONFIGS.items():
        total = sum(config["segments"].values())
        print(f"--- Generating {country}: {total} agents ---")
        behaviors = run_country_population(country, config)
        print(f"    Generated {len(behaviors)} agents")

        analysis = analyze_country(country, behaviors)
        all_results[country] = analysis
        all_behaviors[country] = behaviors

    # =========================================================================
    # RESULTS
    # =========================================================================

    print()
    print("=" * 80)
    print("BEHAVIORAL CASCADE RESULTS")
    print("=" * 80)

    for country, r in all_results.items():
        print(f"\n{'=' * 60}")
        print(f"  {country.upper()} ({r['total_agents']} agents)")
        print(f"{'=' * 60}")

        print(f"\n  Dominant Emotion per Segment:")
        for seg, data in r["segment_dominant_emotion"].items():
            bar = "#" * int(data["pct"] / 5)
            print(f"    {seg:20s} -> {data['emotion']:14s} ({data['pct']:5.1f}% of {data['total']}) {bar}")

        print(f"\n  Overall Emotion Distribution:")
        for emotion, count in r["emotion_distribution"].items():
            pct = count / r["total_agents"] * 100
            bar = "#" * int(pct / 3)
            print(f"    {emotion:14s}: {count:4d} ({pct:5.1f}%) {bar}")

        print(f"\n  Action Distribution:")
        for action, count in r["action_distribution"].items():
            pct = count / r["total_agents"] * 100
            print(f"    {action:20s}: {count:4d} ({pct:5.1f}%)")

        print(f"\n  Cascade Metrics:")
        print(f"    Share Rate:         {r['share_rate']:.1f}%")
        print(f"    Active Sharers:     {r['sharers_count']} / {r['total_agents']}")
        print(f"    Amplifier Nodes:    {r['amplifier_count']} ({r['amplifier_pct']:.1f}%)")
        print(f"    Total Cascade:      {r['total_cascade_reach']:,}")
        print(f"    Avg Reach/Agent:    {r['avg_cascade_per_agent']}")
        print(f"    Avg Trust Govt:     {r['avg_trust_government']:.1f}/10")

        if r["amplifier_nodes"]:
            print(f"\n  Top Amplifier Nodes:")
            for name, seg, occ, reach in r["amplifier_nodes"]:
                print(f"    {name:25s} [{seg:15s}] {occ[:35]:35s} reach={reach}")

        print_sample_posts(all_behaviors[country], country, n=4)

    # =========================================================================
    # CROSS-COUNTRY COMPARISON
    # =========================================================================

    print()
    print("=" * 80)
    print("CROSS-COUNTRY COMPARISON")
    print("=" * 80)

    print(f"\n  {'Country':<15s} {'Agents':<8s} {'Share%':<8s} {'Amps':<6s} {'Amp%':<6s} {'Cascade':<10s} {'Trust':<6s} {'Top Emotion':<15s}")
    print(f"  {'-'*74}")
    for country, r in all_results.items():
        top_emotion = max(r["emotion_distribution"], key=r["emotion_distribution"].get)
        print(f"  {country:<15s} {r['total_agents']:<8d} {r['share_rate']:<8.1f} {r['amplifier_count']:<6d} {r['amplifier_pct']:<6.1f} {r['total_cascade_reach']:<10,d} {r['avg_trust_government']:<6.1f} {top_emotion:<15s}")

    # Vulnerability ranking
    print(f"\n  VULNERABILITY RANKING (by share rate * amplifier density):")
    ranked = sorted(all_results.items(), key=lambda x: x[1]["share_rate"] * x[1]["amplifier_pct"], reverse=True)
    for i, (country, r) in enumerate(ranked, 1):
        vuln_score = r["share_rate"] * r["amplifier_pct"]
        print(f"    {i}. {country:<15s} vulnerability_score={vuln_score:.1f}")

    # Total cascade
    total_agents = sum(r["total_agents"] for r in all_results.values())
    total_cascade = sum(r["total_cascade_reach"] for r in all_results.values())
    total_amps = sum(r["amplifier_count"] for r in all_results.values())
    print(f"\n  TOTAL: {total_agents} agents | {total_cascade:,} cascade reach | {total_amps} amplifier nodes")

    print(f"\n{'=' * 80}")
    print("SIMULATION COMPLETE")
    print(f"{'=' * 80}")
