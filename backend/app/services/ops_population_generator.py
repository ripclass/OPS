"""
OPS-native population generation service.
"""

import concurrent.futures
import json
import math
import random
import re
import unicodedata
from typing import Any, Dict, List, Optional

from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger
from .oasis_profile_generator import OasisAgentProfile, OasisProfileGenerator
from .zep_entity_reader import EntityNode

logger = get_logger("ops.population")


SEGMENT_ALIASES = {
    "rural": "rural",
    "urban working class": "urban_working",
    "urban_working": "urban_working",
    "urban-working": "urban_working",
    "middle class": "middle_class",
    "middle_class": "middle_class",
    "middle-class": "middle_class",
    "corporate": "corporate",
    "migration workers": "migration_workers",
    "migration worker": "migration_workers",
    "migration_workers": "migration_workers",
    "migration-workers": "migration_workers",
    "students": "students",
    "student": "students",
    "women": "women",
    "woman": "women",
    "elderly": "elderly",
    "elder": "elderly",
}

RUN_TYPE_ALIASES = {
    "domestic": "Domestic",
    "diaspora": "Diaspora",
    "corridor-based": "Corridor-based",
    "corridor_based": "Corridor-based",
    "regional multi-country": "Regional multi-country",
    "regional_multi_country": "Regional multi-country",
    "regional-multi-country": "Regional multi-country",
}

COUNTRY_ALIASES = {
    "bangladesh": "Bangladesh",
    "india": "India",
    "pakistan": "Pakistan",
    "nepal": "Nepal",
    "sri lanka": "Sri Lanka",
    "srilanka": "Sri Lanka",
    "sri_lanka": "Sri Lanka",
}

GENERIC_SEGMENT_RULES = {
    "rural": "Rural agents should reflect higher food and transport vulnerability, tighter community visibility, and stronger shame pressure.",
    "urban_working": "Urban working-class agents should show wage, rent, or utility pressure and dense peer influence.",
    "middle_class": "Middle-class agents should balance cost anxiety, family status, and long-term stability.",
    "corporate": "Corporate agents should feel more polished, professionally cautious, and income-stable.",
    "migration_workers": "Migration workers should show remittance obligations, family separation, and job-security anxiety.",
    "students": "Students should have high platform intensity, faster peer amplification, and more rumor exposure.",
    "women": "Women-specific agents should reflect gendered safety, household, and reputation pressures.",
    "elderly": "Elderly agents should show lower posting intensity, stronger memory of past shocks, and slower but durable opinion change.",
}

COUNTRY_SETTINGS: Dict[str, Dict[str, Any]] = {
    "Bangladesh": {
        "segment_weights": {
            "rural": 0.38,
            "urban_working": 0.22,
            "middle_class": 0.15,
            "corporate": 0.05,
            "migration_workers": 0.08,
            "students": 0.07,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "dhaka": "Dhaka division with dense urban neighborhoods, formal and informal employment, and fast rumor circulation.",
            "chittagong": "Chittagong with port-city trade, transport corridors, and Chatgaayan speech influence.",
            "sylhet": "Sylhet with migration ties, remittance culture, and Sylheti linguistic identity.",
            "rajshahi": "Rajshahi with education-centered public life and agricultural surroundings.",
            "barisal": "Barisal with river-linked mobility and stronger local visibility.",
            "khulna": "Khulna with industrial pressure, climate vulnerability, and mixed urban-rural influence.",
            "mixed": "A mixed Bangladesh sample across Dhaka, Chittagong, Sylhet, Rajshahi, Barisal, and Khulna.",
        },
        "dialects": "Use only Bangladesh-relevant varieties such as standard Dhaka Bangla, Sylheti, Chatgaayan, Noakhali-influenced Bangla, or Barishal speech.",
        "country_rules": [
            "Garments and transport-linked workers should show cost pressure and lower trust in official relief promises.",
            "Migration-linked households should reflect remittance pressure, Gulf labour exposure, and family-status obligations.",
            "Rural households should feel food-price shocks quickly and often avoid public shame or visible conflict.",
        ],
    },
    "India": {
        "segment_weights": {
            "rural": 0.33,
            "urban_working": 0.24,
            "middle_class": 0.18,
            "corporate": 0.08,
            "migration_workers": 0.05,
            "students": 0.07,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "delhi": "Delhi NCR with political discourse, class layering, and Hindi-English public speech.",
            "mumbai": "Mumbai with service-sector pressure, commuting stress, and mixed-language urban discourse.",
            "kolkata": "Kolkata with Bengali public culture, education-oriented middle class, and political memory.",
            "chennai": "Chennai with Tamil speech patterns, family reputation concerns, and strong education pressure.",
            "bengaluru": "Bengaluru with IT/corporate discourse, migrant professionals, and English-heavy online behavior.",
            "hyderabad": "Hyderabad with mixed Telugu-Urdu-English influence, tech labor, and migration-linked middle classes.",
            "mixed": "A mixed India sample across Delhi, Mumbai, Kolkata, Chennai, Bengaluru, and Hyderabad.",
        },
        "dialects": "Use India-relevant speech styles such as Bengali, Hindi-English mix, Tamil-English mix, Telugu-English mix, or regional colloquial English.",
        "country_rules": [
            "Corporate and professional agents should sound more LinkedIn-like and class-aware.",
            "Students should show higher meme fluency, peer amplification, and region/language identity.",
            "Rural and urban working agents should reflect inflation, fuel, wages, and family obligations more than abstract macro talk.",
        ],
    },
    "Pakistan": {
        "segment_weights": {
            "rural": 0.35,
            "urban_working": 0.23,
            "middle_class": 0.16,
            "corporate": 0.06,
            "migration_workers": 0.08,
            "students": 0.07,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "karachi": "Karachi with high cost pressure, ethnic layering, fast rumor spread, and Urdu-English public discourse.",
            "lahore": "Lahore with Punjabi/Urdu culture, middle-class education pressure, and expressive public debate.",
            "islamabad": "Islamabad-Rawalpindi with state proximity, salaried households, and more formal discourse.",
            "peshawar": "Peshawar with stronger family and community honor structures and Pashto-influenced speech.",
            "faisalabad": "Faisalabad with industrial labor, business-family networks, and cost-of-living stress.",
            "mixed": "A mixed Pakistan sample across Karachi, Lahore, Islamabad-Rawalpindi, Peshawar, and Faisalabad.",
        },
        "dialects": "Use Pakistan-relevant styles such as Karachi Urdu, Punjabi-influenced Urdu, Pashto-influenced Urdu, or English-Urdu mix.",
        "country_rules": [
            "Working households should reflect inflation and utility strain directly.",
            "Migration-linked households should often connect to Gulf labor and remittance exposure.",
            "Honor, respectability, and visible criticism should matter more for many conservative segments.",
        ],
    },
    "Nepal": {
        "segment_weights": {
            "rural": 0.40,
            "urban_working": 0.20,
            "middle_class": 0.16,
            "corporate": 0.05,
            "migration_workers": 0.10,
            "students": 0.05,
            "women": 0.02,
            "elderly": 0.02,
        },
        "regions": {
            "kathmandu": "Kathmandu Valley with urban youth, education pressure, and Nepali-English public discourse.",
            "pokhara": "Pokhara with tourism-linked employment, migration ties, and mixed urban-rural identity.",
            "terai": "Terai with plains politics, cross-border movement, and Maithili/Bhojpuri influence.",
            "biratnagar": "Biratnagar with industrial labor, migration, and eastern urban networks.",
            "nepalgunj": "Nepalgunj with migration and border-linked livelihood pressure.",
            "mixed": "A mixed Nepal sample across Kathmandu Valley, Pokhara, Terai, Biratnagar, and Nepalgunj.",
        },
        "dialects": "Use Nepal-relevant styles such as Kathmandu Nepali, Maithili/Bhojpuri-influenced Nepali, or Nepali-English mix.",
        "country_rules": [
            "Migration work should be prominent, especially Gulf and Malaysia labor links.",
            "Rural agents should reflect agricultural pressure, remittance dependence, and family hierarchy.",
            "Urban youth should mix aspiration, migration ambition, and social-media mimicry.",
        ],
    },
    "Sri Lanka": {
        "segment_weights": {
            "rural": 0.30,
            "urban_working": 0.24,
            "middle_class": 0.19,
            "corporate": 0.08,
            "migration_workers": 0.08,
            "students": 0.06,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "colombo": "Colombo with urban middle classes, political memory, and Sinhala-English discourse.",
            "kandy": "Kandy with education-linked households, middle-class status concerns, and Sinhala speech.",
            "galle": "Galle with tourism-linked work, coastal livelihoods, and mixed class pressure.",
            "jaffna": "Jaffna with Tamil identity, historical memory, and stronger diaspora linkage.",
            "batticaloa": "Batticaloa with Tamil-speaking eastern networks and livelihood insecurity.",
            "mixed": "A mixed Sri Lanka sample across Colombo, Kandy, Galle, Jaffna, and Batticaloa.",
        },
        "dialects": "Use Sri Lanka-relevant styles such as Sinhala urban speech, Tamil Jaffna style, or Sinhala/Tamil-English mix.",
        "country_rules": [
            "Economic memory and political trust volatility should still matter for many segments.",
            "Tamil-majority and diaspora-linked communities may show stronger conflict-memory sensitivity.",
            "Corporate and urban middle classes should display more formal, polished public signaling.",
        ],
    },
}

DIASPORA_REGION_SETTINGS = {
    "gulf": "Gulf migrant and family-remittance networks across Saudi Arabia, UAE, Qatar, Kuwait, Oman, and Bahrain.",
    "uk": "United Kingdom diaspora communities with intergenerational identity tension and political discussion tied back home.",
    "eu": "European diaspora communities with mixed labor and professional migration patterns.",
    "us": "United States diaspora communities with class-diverse, education-heavy, and transnational identity patterns.",
    "north america": "North American diaspora communities across the United States and Canada.",
    "southeast asia": "Diaspora communities across Malaysia, Singapore, and nearby labor corridors.",
    "mixed": "A mixed diaspora sample across Gulf, UK, EU, and US communities.",
}

MIXED_SOUTH_ASIA_WEIGHTS = {
    "Bangladesh": 0.22,
    "India": 0.42,
    "Pakistan": 0.20,
    "Nepal": 0.08,
    "Sri Lanka": 0.05,
    "Diaspora": 0.03,
}

OPS_SEGMENT_ENTITY_TYPES = {
    "rural": "RuralHousehold",
    "urban_working": "UrbanWorkingFamily",
    "middle_class": "MiddleClassFamily",
    "corporate": "CorporateProfessional",
    "migration_workers": "MigrationWorker",
    "students": "Student",
    "women": "WomenHouseholdVoice",
    "elderly": "ElderlyCitizen",
}


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return value or "ops_agent"


def _coerce_int(value: Any, default: int) -> int:
    try:
        parsed = int(float(value))
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def normalize_ops_population_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Normalize structured OPS population params from the frontend into backend-safe values."""
    if not isinstance(params, dict) or not params:
        return None

    raw_run_type = str(params.get("run_type") or params.get("runType") or "Domestic").strip()
    run_type = RUN_TYPE_ALIASES.get(raw_run_type.lower(), raw_run_type if raw_run_type in RUN_TYPE_ALIASES.values() else "Domestic")

    origin_country_raw = str(params.get("origin_country") or params.get("originCountry") or params.get("country") or "Bangladesh").strip()
    origin_country = COUNTRY_ALIASES.get(origin_country_raw.lower(), origin_country_raw if origin_country_raw in COUNTRY_SETTINGS else "Bangladesh")

    origin_countries_raw = params.get("origin_countries") or params.get("originCountries") or params.get("countries") or []
    origin_countries = []
    for item in origin_countries_raw if isinstance(origin_countries_raw, list) else []:
        normalized = COUNTRY_ALIASES.get(str(item).strip().lower())
        if normalized and normalized not in origin_countries:
            origin_countries.append(normalized)

    raw_segments = params.get("segments") or []
    segments = []
    if isinstance(raw_segments, list):
        for item in raw_segments:
            normalized = SEGMENT_ALIASES.get(str(item).strip().lower())
            if normalized and normalized not in segments:
                segments.append(normalized)

    requested_outputs = []
    raw_outputs = params.get("requested_outputs") or params.get("requestedOutputs") or []
    if isinstance(raw_outputs, list):
        requested_outputs = [str(item).strip() for item in raw_outputs if str(item).strip()]

    audience_region = str(params.get("audience_region") or params.get("audienceRegion") or "").strip()
    corridor = str(params.get("corridor") or "").strip()
    region = str(params.get("region") or "mixed").strip() or "mixed"

    normalized = {
        "run_type": run_type,
        "origin_country": origin_country,
        "origin_countries": origin_countries,
        "audience_region": audience_region,
        "corridor": corridor,
        "segments": segments,
        "n_agents": _coerce_int(params.get("n_agents") or params.get("nAgents") or params.get("target_agents") or params.get("targetAgents"), 100),
        "requested_outputs": requested_outputs,
        "region": region,
    }

    if not normalized["segments"]:
        return None

    if run_type == "Regional multi-country" and len(origin_countries) < 2:
        return None
    if run_type == "Diaspora" and not audience_region:
        normalized["audience_region"] = "Gulf"
    if run_type == "Corridor-based" and not corridor:
        normalized["corridor"] = f"{origin_country} corridor"

    return normalized


class OPSPopulationGenerator:
    """Generate OPS-native populations directly from population parameters."""

    MAX_WORKERS = 10

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.profile_helper = OasisProfileGenerator(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name=self.model_name,
        )

    def generate_population(
        self,
        params: Dict[str, Any],
        scenario_context: str,
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        """Dispatch OPS-native population generation by run type and geography."""
        normalized = normalize_ops_population_params(params)
        if not normalized:
            raise ValueError("OPS population params are missing required fields")

        run_type = normalized["run_type"]
        n_agents = normalized["n_agents"]
        segments = normalized["segments"]

        if run_type == "Domestic":
            return self._dispatch_country_population(
                country=normalized["origin_country"],
                n_agents=n_agents,
                segments=segments,
                scenario_context=scenario_context,
                region=normalized["region"],
                use_llm=use_llm,
            )

        if run_type == "Diaspora":
            return self.generate_diaspora_population(
                n_agents=n_agents,
                segments=segments,
                scenario_context=scenario_context,
                audience_region=normalized["audience_region"],
                origin_country=normalized["origin_country"],
                use_llm=use_llm,
            )

        if run_type == "Corridor-based":
            return self.generate_diaspora_population(
                n_agents=n_agents,
                segments=segments,
                scenario_context=f"{scenario_context}\nCorridor: {normalized['corridor']}",
                audience_region=normalized["audience_region"] or "mixed",
                origin_country=normalized["origin_country"],
                use_llm=use_llm,
            )

        return self.generate_mixed_south_asia_population(
            n_agents=n_agents,
            segments=segments,
            scenario_context=scenario_context,
            countries=normalized["origin_countries"],
            use_llm=use_llm,
        )

    def generate_bangladesh_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Bangladesh", n_agents, segments, scenario_context, region, use_llm)

    def generate_india_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("India", n_agents, segments, scenario_context, region, use_llm)

    def generate_pakistan_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Pakistan", n_agents, segments, scenario_context, region, use_llm)

    def generate_nepal_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Nepal", n_agents, segments, scenario_context, region, use_llm)

    def generate_srilanka_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Sri Lanka", n_agents, segments, scenario_context, region, use_llm)

    def generate_diaspora_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        audience_region: str = "Gulf",
        origin_country: str = "Bangladesh",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        normalized_country = COUNTRY_ALIASES.get(str(origin_country).strip().lower(), origin_country if origin_country in COUNTRY_SETTINGS else "Bangladesh")
        normalized_region = str(audience_region or "mixed").strip() or "mixed"
        settings = COUNTRY_SETTINGS.get(normalized_country, COUNTRY_SETTINGS["Bangladesh"])
        assignments = self._build_segment_assignments(n_agents, segments, settings["segment_weights"])
        diaspora_context = DIASPORA_REGION_SETTINGS.get(normalized_region.lower(), DIASPORA_REGION_SETTINGS["mixed"])

        profiles: List[OasisAgentProfile] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, max(1, len(assignments)))) as executor:
            futures = [
                executor.submit(
                    self._generate_ops_agent_from_demographics,
                    country=normalized_country,
                    segment=segment,
                    region=normalized_region,
                    agent_index=idx,
                    scenario_context=scenario_context,
                    use_llm=use_llm,
                    diaspora_region=normalized_region,
                    diaspora_context=diaspora_context,
                )
                for idx, segment in enumerate(assignments)
            ]
            for future in concurrent.futures.as_completed(futures):
                profiles.append(future.result())

        profiles.sort(key=lambda profile: profile.user_id)
        return profiles

    def generate_mixed_south_asia_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        countries: Optional[List[str]] = None,
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        included = [COUNTRY_ALIASES.get(str(country).strip().lower(), str(country).strip()) for country in (countries or [])]
        included = [country for country in included if country in COUNTRY_SETTINGS]
        include_diaspora = not included
        if not included:
            included = ["Bangladesh", "India", "Pakistan", "Nepal", "Sri Lanka"]

        weights = {country: MIXED_SOUTH_ASIA_WEIGHTS.get(country, 0.0) for country in included}
        if include_diaspora:
            weights["Diaspora"] = MIXED_SOUTH_ASIA_WEIGHTS["Diaspora"]
        weights = self._normalize_weight_subset(weights)

        allocations = self._allocate_weighted_counts(n_agents, weights)
        combined: List[OasisAgentProfile] = []

        for country, count in allocations.items():
            if count <= 0:
                continue
            if country == "Diaspora":
                combined.extend(
                    self.generate_diaspora_population(
                        n_agents=count,
                        segments=segments,
                        scenario_context=scenario_context,
                        audience_region="mixed",
                        origin_country=random.choice(included),
                        use_llm=use_llm,
                    )
                )
                continue

            combined.extend(
                self._dispatch_country_population(
                    country=country,
                    n_agents=count,
                    segments=segments,
                    scenario_context=scenario_context,
                    region="mixed",
                    use_llm=use_llm,
                )
            )

        return self._reindex_profiles(combined)

    def build_population_entities(
        self,
        profiles: List[OasisAgentProfile],
    ) -> List[EntityNode]:
        """Build synthetic population entities so config generation matches OPS profile scale."""
        entities: List[EntityNode] = []
        for profile in profiles:
            segment = profile.source_entity_type or "person"
            entity_labels = self._segment_to_entity_labels(segment)
            entity_type = next((label for label in entity_labels if label not in {"Entity", "Person", "Node"}), "Person")
            summary = (
                f"{profile.name} is a {profile.profession or 'person'} from {profile.location or profile.country or 'South Asia'}"
                f" speaking as a {entity_type} archetype in the simulation."
                f" Segment={segment},"
                f" with trust_government={profile.current_trust_government if profile.current_trust_government is not None else profile.trust_government},"
                f" shame_sensitivity={profile.current_shame_sensitivity if profile.current_shame_sensitivity is not None else profile.shame_sensitivity},"
                f" primary_fear={profile.primary_fear or 'unclear'}, dialect={profile.dialect or 'unspecified'},"
                f" fb_intensity={profile.fb_intensity if profile.fb_intensity is not None else 'unknown'}."
            )
            entities.append(
                EntityNode(
                    uuid=profile.source_entity_uuid or f"ops_profile_{profile.user_id}",
                    name=profile.name,
                    labels=entity_labels,
                    summary=summary,
                    attributes={
                        "segment": segment,
                        "voice_archetype": entity_type,
                        "profession": profile.profession,
                        "country": profile.country,
                        "location": getattr(profile, "location", None),
                        "dialect": profile.dialect,
                        "primary_fear": profile.primary_fear,
                        "influence_radius": profile.influence_radius,
                    },
                )
            )
        return entities

    def _dispatch_country_population(
        self,
        country: str,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str,
        use_llm: bool,
    ) -> List[OasisAgentProfile]:
        if country == "Bangladesh":
            return self.generate_bangladesh_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "India":
            return self.generate_india_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "Pakistan":
            return self.generate_pakistan_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "Nepal":
            return self.generate_nepal_population(n_agents, segments, scenario_context, region, use_llm)
        return self.generate_srilanka_population(n_agents, segments, scenario_context, region, use_llm)

    def _generate_country_population(
        self,
        country: str,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str,
        use_llm: bool,
    ) -> List[OasisAgentProfile]:
        settings = COUNTRY_SETTINGS[country]
        assignments = self._build_segment_assignments(n_agents, segments, settings["segment_weights"])
        normalized_region = self._normalize_region(settings["regions"], region)

        profiles: List[OasisAgentProfile] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, max(1, len(assignments)))) as executor:
            futures = [
                executor.submit(
                    self._generate_ops_agent_from_demographics,
                    country=country,
                    segment=segment,
                    region=normalized_region,
                    agent_index=idx,
                    scenario_context=scenario_context,
                    use_llm=use_llm,
                )
                for idx, segment in enumerate(assignments)
            ]
            for future in concurrent.futures.as_completed(futures):
                profiles.append(future.result())

        profiles.sort(key=lambda profile: profile.user_id)
        return profiles

    def _generate_ops_agent_from_demographics(
        self,
        country: str,
        segment: str,
        region: str,
        agent_index: int,
        scenario_context: str,
        use_llm: bool = True,
        diaspora_region: Optional[str] = None,
        diaspora_context: Optional[str] = None,
    ) -> OasisAgentProfile:
        if not use_llm:
            profile_data = self._generate_fallback_profile(country, segment, region, agent_index, diaspora_region)
        else:
            prompt = self._build_population_prompt(
                country=country,
                segment=segment,
                region=region,
                scenario_context=scenario_context,
                diaspora_region=diaspora_region,
                diaspora_context=diaspora_context,
            )
            system_prompt = (
                "You are an OPS population generation expert. Generate one authentic, specific South Asian person for a behavioral public-opinion simulation. "
                "Return a single valid JSON object only. String values must not contain unescaped newlines. Use English except for names, locations, and dialect labels where appropriate."
            )

            max_attempts = 3
            last_error = None
            profile_data: Optional[Dict[str, Any]] = None

            for attempt in range(max_attempts):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                        temperature=max(0.3, 0.7 - (attempt * 0.1)),
                    )
                    content = response.choices[0].message.content
                    if response.choices[0].finish_reason == "length":
                        content = self.profile_helper._fix_truncated_json(content)

                    try:
                        profile_data = json.loads(content)
                    except json.JSONDecodeError:
                        repaired = self.profile_helper._try_fix_json(
                            content=content,
                            entity_name=f"{country}_{segment}_{agent_index}",
                            entity_type=segment,
                            entity_summary=scenario_context[:200],
                        )
                        if repaired.get("_fixed"):
                            repaired.pop("_fixed", None)
                        profile_data = repaired

                    if profile_data:
                        break
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        f"OPS population generation failed for {country}/{segment} agent {agent_index} on attempt {attempt + 1}: {exc}"
                    )

            if not profile_data:
                logger.warning(
                    f"Falling back to rule-based OPS profile for {country}/{segment} agent {agent_index}: {last_error}"
                )
                profile_data = self._generate_fallback_profile(country, segment, region, agent_index, diaspora_region)

        return self._build_profile(
            country=country,
            segment=segment,
            agent_index=agent_index,
            region=region,
            profile_data=profile_data,
            diaspora_region=diaspora_region,
        )

    def _build_population_prompt(
        self,
        country: str,
        segment: str,
        region: str,
        scenario_context: str,
        diaspora_region: Optional[str],
        diaspora_context: Optional[str],
    ) -> str:
        settings = COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])
        region_context = settings["regions"].get(region.lower(), settings["regions"]["mixed"])
        segment_rule = GENERIC_SEGMENT_RULES.get(segment, "The agent should feel like a specific person shaped by class, place, and everyday risk.")
        country_rules = "\n".join(f"- {rule}" for rule in settings["country_rules"])

        diaspora_block = ""
        if diaspora_region:
            diaspora_block = (
                f"\nDiaspora context: {diaspora_context or DIASPORA_REGION_SETTINGS.get(diaspora_region.lower(), DIASPORA_REGION_SETTINGS['mixed'])}\n"
                "- If this person is migration-linked, include current-location abroad or family-remittance obligations in the persona.\n"
                "- Romanized South Asian language mixed with English is acceptable for diaspora identity markers.\n"
            )

        return f"""Generate one authentic {country} person for an OPS behavioral simulation.

Segment: {segment}
Region: {region}
Scenario context: {scenario_context}

Country-specific region context:
{region_context}

Segment rule:
- {segment_rule}

Country rules:
{country_rules}

Dialect guidance:
- {settings['dialects']}
{diaspora_block}
Generate a complete OPS persona as valid JSON with ALL of these fields:
- name: authentic real-world personal name appropriate to religion, class, and region
- age: realistic integer for the segment
- gender: realistic for the segment, usually "male", "female", or "other" if needed
- occupation: specific job title, not generic
- location: specific district/city/locality string appropriate to the region
- trust_government: integer 0-10 based on segment reality
- shame_sensitivity: integer 0-10 based on segment, class, age, and gendered pressure
- primary_fear: specific and personal, not abstract
- influence_radius: realistic integer for the segment
- fb_intensity: integer 0-10 realistic for the segment
- dialect: specific speech style for this person
- income_stability: concrete description of income stability
- rumour_amplifier: boolean true/false based on segment behavior
- baseline_anxiety: number 0-10
- interested_topics: array of recurring topics
- mbti: plausible MBTI shorthand
- bio: exactly 2 sentences written as their social media bio would read
- persona: about 300 words covering daily life, inner fears, social position, family pressure, communication style, and likely reaction patterns

Critical rules:
- All agents must feel like real specific people, not demographic averages.
- Do not output institutions or brand accounts.
- Use the scenario context to sharpen fear, trust, and posting intensity.
- Keep values internally consistent with the segment and country.
- Rural agents should skew toward higher food and transport vulnerability and stronger community pressure.
- Urban working-class agents should show stronger wage, rent, or utility pressure.
- Migration workers should often have remittance obligations and migration anxiety.
- Corporate agents should feel more polished and professionally cautious.
- Students should have high social intensity and rumor exposure.
- Elderly women should have low posting intensity and high shame pressure when appropriate.

Return valid JSON only."""

    def _build_profile(
        self,
        country: str,
        segment: str,
        agent_index: int,
        region: str,
        profile_data: Dict[str, Any],
        diaspora_region: Optional[str],
    ) -> OasisAgentProfile:
        name = str(profile_data.get("name") or f"{country} Citizen {agent_index + 1}").strip()
        user_name = self._generate_username(name, agent_index)
        trust = OasisAgentProfile._clamp_int(profile_data.get("trust_government"), 0, 10)
        shame = OasisAgentProfile._clamp_int(profile_data.get("shame_sensitivity"), 0, 10)
        baseline_anxiety = OasisAgentProfile._clamp_float(profile_data.get("baseline_anxiety", 5.0), 0.0, 10.0)

        profile = OasisAgentProfile(
            user_id=agent_index,
            user_name=user_name,
            name=name,
            bio=str(profile_data.get("bio") or f"{name} is part of the {segment} segment in {country}.").strip(),
            persona=str(profile_data.get("persona") or f"{name} is a socially active {segment} citizen in {country}.").strip(),
            karma=random.randint(500, 4000),
            friend_count=random.randint(40, 400),
            follower_count=random.randint(80, 1200),
            statuses_count=random.randint(80, 1800),
            age=OasisAgentProfile._clamp_int(profile_data.get("age"), 13, 100),
            gender=str(profile_data.get("gender") or "other").strip().lower(),
            mbti=str(profile_data.get("mbti") or random.choice(self.profile_helper.MBTI_TYPES)).strip(),
            country=country,
            location=str(profile_data.get("location") or f"{country} ({region})").strip(),
            profession=str(profile_data.get("occupation") or profile_data.get("profession") or "Unknown").strip(),
            interested_topics=self._coerce_topics(profile_data.get("interested_topics")),
            trust_government=trust,
            shame_sensitivity=shame,
            primary_fear=str(profile_data.get("primary_fear") or "income insecurity").strip(),
            influence_radius=OasisAgentProfile._clamp_int(profile_data.get("influence_radius"), 0, 1_000_000),
            fb_intensity=OasisAgentProfile._clamp_int(profile_data.get("fb_intensity"), 0, 10),
            dialect=str(profile_data.get("dialect") or region).strip(),
            income_stability=str(profile_data.get("income_stability") or "variable").strip(),
            rumour_amplifier=self._coerce_bool(profile_data.get("rumour_amplifier")),
            migration_worker_flag=self._coerce_bool(profile_data.get("migration_worker_flag"), default=segment == "migration_workers"),
            remittance_dependency_flag=self._coerce_bool(
                profile_data.get("remittance_dependency_flag"),
                default=segment == "migration_workers" or bool(diaspora_region),
            ),
            baseline_anxiety=baseline_anxiety,
            source_entity_uuid=f"ops_population_{country.lower().replace(' ', '_')}_{agent_index}",
            source_entity_type=segment,
        )

        if trust is not None:
            profile.current_trust_government = trust
        if shame is not None:
            profile.current_shame_sensitivity = shame

        return profile

    def _generate_fallback_profile(
        self,
        country: str,
        segment: str,
        region: str,
        agent_index: int,
        diaspora_region: Optional[str],
    ) -> Dict[str, Any]:
        settings = COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])
        gender = random.choice(["male", "female"])
        name_pool = {
            "Bangladesh": {
                "male": ["Rahim Hasan", "Sajjad Hossain", "Imran Kabir", "Masud Rana"],
                "female": ["Ayesha Akter", "Ruma Khatun", "Farzana Rahman", "Sharmin Sultana"],
            },
            "India": {
                "male": ["Rahul Sharma", "Amit Das", "Arjun Nair", "Sandeep Kumar"],
                "female": ["Priya Sen", "Ananya Roy", "Meera Nair", "Kavya Iyer"],
            },
            "Pakistan": {
                "male": ["Ali Raza", "Usman Ahmed", "Bilal Khan", "Hamza Qureshi"],
                "female": ["Ayesha Noor", "Hira Malik", "Sana Javed", "Maham Raza"],
            },
            "Nepal": {
                "male": ["Suman Karki", "Ramesh Thapa", "Bikash Gurung", "Dipesh Yadav"],
                "female": ["Sita Thapa", "Anjana Koirala", "Mina Gurung", "Rita Yadav"],
            },
            "Sri Lanka": {
                "male": ["Nimal Perera", "Suren Fernando", "Sivakumar Rajan", "Kasun Jayasekara"],
                "female": ["Dilani Perera", "Nadeesha Silva", "Kavitha Rajan", "Ishara Fernando"],
            },
        }
        job_pool = {
            "rural": ["small farmer", "fish trader", "village shopkeeper", "day laborer"],
            "urban_working": ["garments worker", "rickshaw driver", "CNG driver", "market helper"],
            "middle_class": ["school teacher", "office clerk", "NGO field officer", "bank assistant"],
            "corporate": ["operations manager", "HR executive", "software analyst", "brand manager"],
            "migration_workers": ["construction worker abroad", "domestic worker abroad", "factory worker abroad", "airport cleaner abroad"],
            "students": ["university student", "college student", "private university student", "coaching student"],
            "women": ["home-based tailor", "school mother", "informal vendor", "community volunteer"],
            "elderly": ["retired school staff", "retired trader", "elder family caretaker", "pensioner"],
        }
        name = random.choice(name_pool.get(country, name_pool["Bangladesh"])[gender])
        job = random.choice(job_pool.get(segment, job_pool["middle_class"]))
        location = diaspora_region or f"{country} ({region})"
        dialect_default = settings["dialects"].split(" such as ")[-1].split(",")[0]

        bio = f"{job.title()} from {location}. Trying to keep family stability and dignity intact during uncertain times."
        persona = (
            f"{name} is a {job} from {location}. This person watches prices, family obligations, and public reputation closely. "
            f"They speak in a style shaped by {dialect_default} and react to social pressure quickly when household stability is threatened. "
            f"Their fear is practical rather than abstract, and their online behavior reflects class position, local rumor exposure, and everyday survival concerns."
        )
        return {
            "name": name,
            "age": random.randint(20, 55) if segment not in {"students", "elderly"} else (random.randint(18, 26) if segment == "students" else random.randint(60, 78)),
            "gender": gender,
            "occupation": job,
            "location": location,
            "trust_government": random.randint(2, 7),
            "shame_sensitivity": random.randint(4, 9 if segment in {"rural", "women", "elderly"} else 7),
            "primary_fear": random.choice(["price shock", "job loss", "family embarrassment", "rent and food costs", "remittance disruption"]),
            "influence_radius": random.randint(8, 120),
            "fb_intensity": random.randint(2, 9 if segment in {"students", "urban_working"} else 6),
            "dialect": dialect_default,
            "income_stability": "stable salary" if segment in {"corporate", "middle_class"} else "fragile and month-to-month",
            "rumour_amplifier": segment in {"students", "urban_working"} and random.random() > 0.45,
            "baseline_anxiety": round(random.uniform(4.0, 8.2), 1),
            "interested_topics": ["family costs", "local news", "social issues"],
            "mbti": random.choice(self.profile_helper.MBTI_TYPES),
            "bio": bio,
            "persona": persona,
            "migration_worker_flag": segment == "migration_workers" or bool(diaspora_region),
            "remittance_dependency_flag": segment == "migration_workers" or bool(diaspora_region),
        }

    def _build_segment_assignments(
        self,
        n_agents: int,
        segments: List[str],
        weights: Dict[str, float],
    ) -> List[str]:
        normalized_segments = [segment for segment in (SEGMENT_ALIASES.get(str(item).strip().lower()) for item in segments) if segment in weights]
        normalized_segments = list(dict.fromkeys(normalized_segments))
        if not normalized_segments:
            normalized_segments = ["rural", "urban_working"]

        selected_weights = self._normalize_weight_subset({segment: weights[segment] for segment in normalized_segments})
        allocations = self._allocate_weighted_counts(n_agents, selected_weights)

        assignments: List[str] = []
        for segment, count in allocations.items():
            assignments.extend([segment] * count)
        random.shuffle(assignments)
        return assignments

    def _normalize_weight_subset(self, weights: Dict[str, float]) -> Dict[str, float]:
        total = sum(max(weight, 0.0) for weight in weights.values())
        if total <= 0:
            even = 1.0 / max(1, len(weights))
            return {key: even for key in weights}
        return {key: max(weight, 0.0) / total for key, weight in weights.items()}

    def _allocate_weighted_counts(self, total_count: int, weights: Dict[str, float]) -> Dict[str, int]:
        allocations: Dict[str, int] = {}
        remainders = []
        assigned = 0
        for key, weight in weights.items():
            raw = total_count * weight
            count = math.floor(raw)
            allocations[key] = count
            assigned += count
            remainders.append((raw - count, key))

        remaining = total_count - assigned
        for _, key in sorted(remainders, reverse=True)[:remaining]:
            allocations[key] += 1
        return allocations

    def _normalize_region(self, region_map: Dict[str, str], region: str) -> str:
        key = str(region or "mixed").strip().lower()
        return key if key in region_map else "mixed"

    def _segment_to_entity_type(self, segment: Optional[str]) -> str:
        normalized = SEGMENT_ALIASES.get(str(segment or "").strip().lower(), str(segment or "").strip().lower())
        return OPS_SEGMENT_ENTITY_TYPES.get(normalized, "Person")

    def _segment_to_entity_labels(self, segment: Optional[str]) -> List[str]:
        primary_type = self._segment_to_entity_type(segment)
        labels = ["Entity", primary_type]
        if primary_type != "Person":
            labels.append("Person")
        deduped: List[str] = []
        for label in labels:
            if label not in deduped:
                deduped.append(label)
        return deduped

    def _generate_username(self, name: str, agent_index: int) -> str:
        return f"{_slugify(name)}_{agent_index:03d}"

    def _coerce_topics(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
        return []

    def _coerce_bool(self, value: Any, default: Optional[bool] = None) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes"}:
                return True
            if lowered in {"false", "0", "no"}:
                return False
        return default

    def _reindex_profiles(self, profiles: List[OasisAgentProfile]) -> List[OasisAgentProfile]:
        for idx, profile in enumerate(profiles):
            profile.user_id = idx
            profile.user_name = self._generate_username(profile.name, idx)
            profile.source_entity_uuid = f"ops_population_{(profile.country or 'south_asia').lower().replace(' ', '_')}_{idx}"
        return profiles
