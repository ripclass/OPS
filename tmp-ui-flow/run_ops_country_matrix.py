import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


BASE_URL = "http://localhost:5001"
OUTPUT_PATH = Path("tmp-ui-flow/country-matrix-summary.json")
TIMEOUT = 900


COUNTRY_RUNS = [
    {
        "country": "Bangladesh",
        "scenario": "Rice prices increase 40% before Eid in Dhaka. How do rural households, urban working families, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Bangladesh",
            "segments": ["rural", "urban_working", "students"],
            "n_agents": 4,
            "requested_outputs": ["PDF report"],
            "region": "dhaka",
        },
    },
    {
        "country": "India",
        "scenario": "Cooking gas cylinder prices increase 25% before Diwali in Kolkata. How do urban working households, middle-class families, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "India",
            "segments": ["urban_working", "middle_class", "students"],
            "n_agents": 4,
            "requested_outputs": ["PDF report"],
            "region": "kolkata",
        },
    },
    {
        "country": "Pakistan",
        "scenario": "Electricity tariffs increase 30% before Eid in Karachi. How do working households, students, and salaried middle-class families respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Pakistan",
            "segments": ["urban_working", "middle_class", "students"],
            "n_agents": 4,
            "requested_outputs": ["PDF report"],
            "region": "karachi",
        },
    },
    {
        "country": "Nepal",
        "scenario": "Rice and cooking oil prices rise sharply before Dashain in Kathmandu. How do rural households, urban workers, and students respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Nepal",
            "segments": ["rural", "urban_working", "students"],
            "n_agents": 4,
            "requested_outputs": ["PDF report"],
            "region": "kathmandu",
        },
    },
    {
        "country": "Sri Lanka",
        "scenario": "Fuel and rice prices rise before Sinhala New Year in Colombo. How do urban working households, middle-class families, and elderly citizens respond over the next 72 hours?",
        "ops_population_params": {
            "run_type": "Domestic",
            "origin_country": "Sri Lanka",
            "segments": ["urban_working", "middle_class", "elderly"],
            "n_agents": 4,
            "requested_outputs": ["PDF report"],
            "region": "colombo",
        },
    },
]


@dataclass
class RunSummary:
    country: str
    scenario: str
    project_id: Optional[str] = None
    graph_task_id: Optional[str] = None
    graph_id: Optional[str] = None
    simulation_id: Optional[str] = None
    prepare_task_id: Optional[str] = None
    report_task_id: Optional[str] = None
    report_id: Optional[str] = None
    profiles_count: int = 0
    profile_countries: Optional[List[str]] = None
    profile_professions: Optional[List[str]] = None
    run_status: Optional[str] = None
    current_round: Optional[int] = None
    total_actions_count: Optional[int] = None
    report_status: Optional[str] = None
    report_chat_ok: bool = False
    interview_ok: bool = False
    interview_error: Optional[str] = None
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


def post_multipart(
    session: requests.Session,
    path: str,
    form_data: Dict[str, Any],
) -> Dict[str, Any]:
    response = session.post(f"{BASE_URL}{path}", data=form_data, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(payload.get("error") or payload)
    return payload["data"]


def poll_graph_task(session: requests.Session, task_id: str, timeout_s: int = 900) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    last_message = ""
    while time.time() < deadline:
        data = get_json(session, f"/api/graph/task/{task_id}")
        if data.get("status") == "completed":
            return data
        if data.get("status") == "failed":
            raise RuntimeError(data.get("message") or "Graph build failed")
        message = data.get("message") or ""
        if message and message != last_message:
            print(f"  [graph] {message}")
            last_message = message
        time.sleep(3)
    raise TimeoutError(f"Graph build timed out for task {task_id}")


def poll_prepare_task(session: requests.Session, simulation_id: str, task_id: str, timeout_s: int = 1800) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    last_message = ""
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
        message = data.get("message") or ""
        if message and message != last_message:
            print(f"  [prepare] {message}")
            last_message = message
        time.sleep(4)
    raise TimeoutError(f"Prepare timed out for simulation {simulation_id}")


def poll_run_complete(session: requests.Session, simulation_id: str, timeout_s: int = 2400) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    last_status = None
    while time.time() < deadline:
        data = get_json(session, f"/api/simulation/{simulation_id}/run-status/detail")
        runner_status = data.get("runner_status")
        if runner_status in {"completed", "failed"}:
            return data
        marker = (runner_status, data.get("current_round"), data.get("progress_percent"))
        if marker != last_status:
            print(
                f"  [run] status={runner_status} round={data.get('current_round')}/{data.get('total_rounds')} "
                f"progress={data.get('progress_percent')}"
            )
            last_status = marker
        time.sleep(6)
    raise TimeoutError(f"Run timed out for simulation {simulation_id}")


def poll_report_complete(
    session: requests.Session,
    simulation_id: str,
    task_id: str,
    timeout_s: int = 1800,
) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    last_message = ""
    while time.time() < deadline:
        data = post_json(
            session,
            "/api/report/generate/status",
            {"simulation_id": simulation_id, "task_id": task_id},
        )
        status = data.get("status")
        if status == "completed":
            return data
        if status == "failed":
            raise RuntimeError(data.get("error") or data.get("message") or "Report failed")
        message = data.get("message") or ""
        if message and message != last_message:
            print(f"  [report] {message}")
            last_message = message
        time.sleep(4)
    raise TimeoutError(f"Report timed out for simulation {simulation_id}")


def fetch_profiles_summary(session: requests.Session, simulation_id: str) -> Dict[str, Any]:
    data = get_json(session, f"/api/simulation/{simulation_id}/profiles/realtime?platform=reddit")
    profiles = data.get("profiles") or data.get("data", {}).get("profiles") or []
    countries = sorted({profile.get("country") for profile in profiles if profile.get("country")})
    professions = [profile.get("profession") for profile in profiles[:5] if profile.get("profession")]
    return {
        "count": len(profiles),
        "countries": countries,
        "professions": professions,
        "profiles": profiles,
    }


def run_country(session: requests.Session, spec: Dict[str, Any]) -> RunSummary:
    summary = RunSummary(country=spec["country"], scenario=spec["scenario"], profile_countries=[], profile_professions=[])
    try:
        print(f"\n=== {spec['country']} ===")
        ontology = post_multipart(
            session,
            "/api/graph/ontology/generate",
            {
                "project_name": f"OPS {spec['country']} Stabilization",
                "simulation_requirement": spec["scenario"],
            },
        )
        summary.project_id = ontology["project_id"]
        print(f"  project={summary.project_id}")

        graph_start = post_json(session, "/api/graph/build", {"project_id": summary.project_id})
        summary.graph_task_id = graph_start["task_id"]
        print(f"  graph task={summary.graph_task_id}")
        graph_result = poll_graph_task(session, summary.graph_task_id)
        summary.graph_id = (graph_result.get("result") or {}).get("graph_id")
        print(f"  graph={summary.graph_id}")

        sim = post_json(
            session,
            "/api/simulation/create",
            {
                "project_id": summary.project_id,
                "ops_population_params": spec["ops_population_params"],
                "enable_twitter": True,
                "enable_reddit": True,
            },
        )
        summary.simulation_id = sim["simulation_id"]
        print(f"  simulation={summary.simulation_id}")

        prepared = post_json(
            session,
            "/api/simulation/prepare",
            {
                "simulation_id": summary.simulation_id,
                "use_llm_for_profiles": True,
                "parallel_profile_count": 5,
                "force_regenerate": True,
                "ops_population_params": spec["ops_population_params"],
            },
        )
        summary.prepare_task_id = prepared["task_id"]
        print(f"  prepare task={summary.prepare_task_id}")
        poll_prepare_task(session, summary.simulation_id, summary.prepare_task_id)

        profiles_summary = fetch_profiles_summary(session, summary.simulation_id)
        summary.profiles_count = profiles_summary["count"]
        summary.profile_countries = profiles_summary["countries"]
        summary.profile_professions = profiles_summary["professions"]
        print(f"  profiles={summary.profiles_count} countries={summary.profile_countries}")

        post_json(
            session,
            "/api/simulation/start",
            {
                "simulation_id": summary.simulation_id,
                "max_rounds": 4,
                "enable_graph_memory_update": False,
            },
        )
        run_result = poll_run_complete(session, summary.simulation_id)
        summary.run_status = run_result.get("runner_status")
        summary.current_round = run_result.get("current_round")
        summary.total_actions_count = run_result.get("total_actions_count")
        print(f"  run status={summary.run_status} actions={summary.total_actions_count}")
        if summary.run_status != "completed":
            raise RuntimeError(f"Simulation ended with runner_status={summary.run_status}")

        report = post_json(
            session,
            "/api/report/generate",
            {"simulation_id": summary.simulation_id, "force_regenerate": True},
        )
        summary.report_task_id = report["task_id"]
        summary.report_id = report["report_id"]
        print(f"  report task={summary.report_task_id} report={summary.report_id}")
        report_status = poll_report_complete(session, summary.simulation_id, summary.report_task_id)
        summary.report_status = report_status.get("status")

        report_chat = post_json(
            session,
            "/api/report/chat",
            {
                "simulation_id": summary.simulation_id,
                "message": "What is the main public reaction in one paragraph?",
                "chat_history": [],
            },
        )
        summary.report_chat_ok = bool((report_chat.get("response") or "").strip())

        interview = post_json(
            session,
            "/api/simulation/interview/batch",
            {
                "simulation_id": summary.simulation_id,
                "interviews": [
                    {
                        "agent_id": 0,
                        "prompt": "What is your first reaction to this situation, and what would you tell your family or friends?",
                    }
                ],
            },
        )
        results = ((interview.get("result") or {}).get("results") or {})
        summary.interview_ok = bool(results)
        if not summary.interview_ok:
            summary.interview_error = "No interview results returned"

        summary.success = True
        return summary
    except Exception as exc:
        summary.error = str(exc)
        return summary


def main() -> int:
    session = requests.Session()
    health = session.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    health.raise_for_status()
    print(f"Health: {health.text}")

    results = [asdict(run_country(session, spec)) for spec in COUNTRY_RUNS]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved summary to {OUTPUT_PATH}")

    failures = [result for result in results if not result.get("success")]
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  - {failure['country']}: {failure.get('error')}")
        return 1

    print("\nAll country runs succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
