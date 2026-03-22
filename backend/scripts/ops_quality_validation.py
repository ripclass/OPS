"""
OPS quality validation harness.

Runs a lightweight end-to-end OPS simulation and scores the result against a
small rubric focused on country fit, seed voice balance, report cleanliness,
and interaction readiness.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


BASE_URL = "http://localhost:5001"
TIMEOUT = 900
REPO_ROOT = Path(__file__).resolve().parents[2]
SIMULATION_ROOT = REPO_ROOT / "backend" / "uploads" / "simulations"
REPORT_ROOT = REPO_ROOT / "backend" / "uploads" / "reports"
INSTITUTIONAL_TYPES = {"GovernmentAgency", "MediaOutlet", "Organization", "Expert"}
SCAFFOLDING_PATTERNS = [
    "tool call",
    "after analyzing",
    "after conducting interviews",
    "next tool:",
    "to gather more detailed",
]

COUNTRY_SPECS: Dict[str, Dict[str, Any]] = {
    "Bangladesh": {
        "scenario": "Rice prices increase 40% before Eid in Dhaka. How do rural households, urban working families, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Bangladesh",
            "segments": ["rural", "urban_working", "students"],
            "n_agents": 8,
            "requested_outputs": ["PDF report"],
            "region": "dhaka",
        },
    },
    "India": {
        "scenario": "Cooking gas cylinder prices increase 25% before Diwali in Kolkata. How do urban working households, middle-class families, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "India",
            "segments": ["urban_working", "middle_class", "students"],
            "n_agents": 8,
            "requested_outputs": ["PDF report"],
            "region": "kolkata",
        },
    },
    "Pakistan": {
        "scenario": "Electricity tariffs increase 30% before Eid in Karachi. How do working households, students, and salaried middle-class families respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Pakistan",
            "segments": ["urban_working", "middle_class", "students"],
            "n_agents": 8,
            "requested_outputs": ["PDF report"],
            "region": "karachi",
        },
    },
    "Nepal": {
        "scenario": "Rice and cooking oil prices rise sharply before Dashain in Kathmandu. How do rural households, urban workers, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Nepal",
            "segments": ["rural", "urban_working", "students"],
            "n_agents": 8,
            "requested_outputs": ["PDF report"],
            "region": "kathmandu",
        },
    },
    "Sri Lanka": {
        "scenario": "Fuel and rice prices rise before Sinhala New Year in Colombo. How do urban working households, middle-class families, and elderly citizens respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Sri Lanka",
            "segments": ["urban_working", "middle_class", "elderly"],
            "n_agents": 8,
            "requested_outputs": ["PDF report"],
            "region": "colombo",
        },
    },
}


@dataclass
class RubricResult:
    country: str
    simulation_id: Optional[str] = None
    report_id: Optional[str] = None
    total_profiles: int = 0
    country_match_ratio: float = 0.0
    segment_coverage_ratio: float = 0.0
    institutional_seed_profiles: int = 0
    institutional_seed_posts: int = 0
    public_seed_posts: int = 0
    institutional_mention_present: bool = False
    report_scaffolding_absent: bool = False
    fake_citation_absent: bool = False
    report_completed: bool = False
    report_chat_ok: bool = False
    interview_ok: bool = False
    score: int = 0
    success: bool = False
    error: Optional[str] = None


def post_json(session: requests.Session, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = session.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get("success", False):
        raise RuntimeError(data.get("error") or data)
    return data["data"]


def get_json(session: requests.Session, path: str) -> Dict[str, Any]:
    response = session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get("success", False):
        raise RuntimeError(data.get("error") or data)
    return data["data"]


def post_multipart(session: requests.Session, path: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
    response = session.post(f"{BASE_URL}{path}", data=form_data, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(payload.get("error") or payload)
    return payload["data"]


def poll_graph_task(session: requests.Session, task_id: str, timeout_s: int = 900) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        data = get_json(session, f"/api/graph/task/{task_id}")
        if data.get("status") == "completed":
            return data
        if data.get("status") == "failed":
            raise RuntimeError(data.get("message") or "Graph build failed")
        time.sleep(3)
    raise TimeoutError(f"Graph build timed out for task {task_id}")


def poll_prepare_task(session: requests.Session, simulation_id: str, task_id: str, timeout_s: int = 1800) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        data = post_json(
            session,
            "/api/simulation/prepare/status",
            {"simulation_id": simulation_id, "task_id": task_id},
        )
        if data.get("status") in {"completed", "ready"} or data.get("already_prepared"):
            return data
        if data.get("status") == "failed":
            raise RuntimeError(data.get("error") or data.get("message") or "Prepare failed")
        time.sleep(4)
    raise TimeoutError(f"Prepare timed out for simulation {simulation_id}")


def poll_run_complete(session: requests.Session, simulation_id: str, timeout_s: int = 2400) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        data = get_json(session, f"/api/simulation/{simulation_id}/run-status/detail")
        if data.get("runner_status") in {"completed", "failed"}:
            return data
        time.sleep(6)
    raise TimeoutError(f"Run timed out for simulation {simulation_id}")


def poll_report_complete(session: requests.Session, simulation_id: str, task_id: str, timeout_s: int = 1800) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        data = post_json(
            session,
            "/api/report/generate/status",
            {"simulation_id": simulation_id, "task_id": task_id},
        )
        if data.get("status") == "completed":
            return data
        if data.get("status") == "failed":
            raise RuntimeError(data.get("error") or data.get("message") or "Report failed")
        time.sleep(4)
    raise TimeoutError(f"Report timed out for simulation {simulation_id}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_score(result: RubricResult) -> int:
    score = 0
    score += 20 if result.country_match_ratio >= 0.9 else int(result.country_match_ratio * 20)
    score += 15 if result.segment_coverage_ratio >= 0.95 else int(result.segment_coverage_ratio * 15)
    score += 10 if result.institutional_seed_profiles >= 1 else 0
    score += 10 if result.institutional_seed_posts >= 1 else 0
    score += 5 if result.public_seed_posts >= 1 else 0
    score += 10 if result.institutional_mention_present else 0
    score += 10 if result.report_scaffolding_absent else 0
    score += 5 if result.fake_citation_absent else 0
    score += 10 if result.report_completed else 0
    score += 5 if result.report_chat_ok else 0
    score += 5 if result.interview_ok else 0
    return min(score, 100)


def validate_country(session: requests.Session, country: str) -> RubricResult:
    spec = COUNTRY_SPECS[country]
    result = RubricResult(country=country)

    try:
        ontology = post_multipart(
            session,
            "/api/graph/ontology/generate",
            {
                "project_name": f"OPS Quality Validation {country}",
                "simulation_requirement": spec["scenario"],
            },
        )
        project_id = ontology["project_id"]

        graph_start = post_json(session, "/api/graph/build", {"project_id": project_id})
        graph_result = poll_graph_task(session, graph_start["task_id"])
        graph_id = (graph_result.get("result") or {}).get("graph_id")
        if not graph_id:
            raise RuntimeError("No graph_id returned from graph build")

        sim = post_json(
            session,
            "/api/simulation/create",
            {
                "project_id": project_id,
                "ops_population_params": spec["ops_population_params"],
                "enable_twitter": True,
                "enable_reddit": True,
            },
        )
        simulation_id = sim["simulation_id"]
        result.simulation_id = simulation_id

        prepared = post_json(
            session,
            "/api/simulation/prepare",
            {
                "simulation_id": simulation_id,
                "use_llm_for_profiles": True,
                "parallel_profile_count": 5,
                "force_regenerate": True,
                "ops_population_params": spec["ops_population_params"],
            },
        )
        poll_prepare_task(session, simulation_id, prepared["task_id"])

        ops_profiles_path = SIMULATION_ROOT / simulation_id / "ops_profiles.json"
        simulation_config_path = SIMULATION_ROOT / simulation_id / "simulation_config.json"
        profiles_payload = load_json(ops_profiles_path)
        simulation_config = load_json(simulation_config_path)
        profiles = profiles_payload if isinstance(profiles_payload, list) else profiles_payload.get("profiles", [])
        selected_segments = set(spec["ops_population_params"]["segments"])

        countries = [profile.get("country") for profile in profiles if profile.get("country")]
        result.total_profiles = len(profiles)
        result.country_match_ratio = (
            sum(1 for value in countries if value == country) / len(countries)
            if countries
            else 0.0
        )

        source_types = [str(profile.get("source_entity_type") or "") for profile in profiles]
        public_types = {value for value in source_types if value not in INSTITUTIONAL_TYPES}
        result.segment_coverage_ratio = (
            len(selected_segments.intersection(public_types)) / len(selected_segments)
            if selected_segments
            else 1.0
        )
        result.institutional_seed_profiles = sum(1 for value in source_types if value in INSTITUTIONAL_TYPES)

        initial_posts = (simulation_config.get("event_config") or {}).get("initial_posts") or []
        poster_types = [str(post.get("poster_type") or "") for post in initial_posts]
        result.institutional_seed_posts = sum(1 for value in poster_types if value in INSTITUTIONAL_TYPES)
        result.public_seed_posts = sum(1 for value in poster_types if value not in INSTITUTIONAL_TYPES)

        post_json(
            session,
            "/api/simulation/start",
            {
                "simulation_id": simulation_id,
                "max_rounds": 4,
                "enable_graph_memory_update": False,
            },
        )
        run_status = poll_run_complete(session, simulation_id)
        if run_status.get("runner_status") != "completed":
            raise RuntimeError(f"Simulation ended with runner_status={run_status.get('runner_status')}")

        report = post_json(
            session,
            "/api/report/generate",
            {"simulation_id": simulation_id, "force_regenerate": True},
        )
        result.report_id = report["report_id"]
        report_status = poll_report_complete(session, simulation_id, report["task_id"])
        result.report_completed = report_status.get("status") == "completed"

        full_report_path = REPORT_ROOT / result.report_id / "full_report.md"
        report_text = full_report_path.read_text(encoding="utf-8")
        report_text_lower = report_text.lower()
        result.report_scaffolding_absent = not any(pattern in report_text_lower for pattern in SCAFFOLDING_PATTERNS)
        result.fake_citation_absent = not bool(re.search(r"\([A-Za-z][^)]*,\s*(19|20)\d{2}\)", report_text))

        institutional_names = [
            str(profile.get("name") or "").strip()
            for profile in profiles
            if str(profile.get("source_entity_type") or "") in INSTITUTIONAL_TYPES
        ]
        result.institutional_mention_present = any(name and name in report_text for name in institutional_names)

        report_chat = post_json(
            session,
            "/api/report/chat",
            {
                "simulation_id": simulation_id,
                "message": "What is the main public reaction in one paragraph?",
                "chat_history": [],
            },
        )
        result.report_chat_ok = bool((report_chat.get("response") or "").strip())

        interview = post_json(
            session,
            "/api/simulation/interview/batch",
            {
                "simulation_id": simulation_id,
                "interviews": [
                    {
                        "agent_id": 0,
                        "prompt": "What is your first reaction to this situation, and what would you tell your family or friends?",
                    }
                ],
            },
        )
        results = ((interview.get("result") or {}).get("results") or {})
        result.interview_ok = bool(results)

        result.score = compute_score(result)
        result.success = (
            result.country_match_ratio >= 0.9
            and result.segment_coverage_ratio >= 0.95
            and result.institutional_seed_posts >= 1
            and result.public_seed_posts >= 1
            and result.report_completed
            and result.report_scaffolding_absent
            and result.fake_citation_absent
            and result.report_chat_ok
            and result.interview_ok
        )
        return result
    except Exception as exc:
        result.error = str(exc)
        result.score = compute_score(result)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OPS quality validation")
    parser.add_argument(
        "--countries",
        nargs="+",
        default=["Bangladesh"],
        choices=sorted(COUNTRY_SPECS.keys()),
        help="Countries to validate",
    )
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "tmp-ui-flow" / "ops-quality-validation.json"),
        help="Where to write the validation summary JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    session = requests.Session()
    health = session.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    health.raise_for_status()

    results = [asdict(validate_country(session, country)) for country in args.countries]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    failures = [item for item in results if not item.get("success")]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
