"""
OPS temporal memory persistence backed by Supabase.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import create_client

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger("ops.memory_store")

_supabase_client = None
_missing_config_logged = False


def _get_client():
    """Create or reuse a Supabase client when temporal storage is configured."""
    global _supabase_client, _missing_config_logged

    if not Config.OPS_MEMORY_STORE_ENABLED:
        if not _missing_config_logged:
            logger.warning("OPS temporal continuity persistence is disabled because SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing.")
            _missing_config_logged = True
        return None

    if _supabase_client is None:
        _supabase_client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _supabase_client


def _build_agent_state_payload(agent, project_id: str) -> Dict[str, Any]:
    """Build the row payload stored in `ops_agent_states`."""
    return {
        "agent_user_id": agent.user_id,
        "project_id": project_id,
        "agent_name": agent.name,
        "simulation_history": agent.simulation_history,
        "baseline_anxiety": agent.baseline_anxiety,
        "current_trust_government": agent.current_trust_government,
        "current_shame_sensitivity": agent.current_shame_sensitivity,
        "cumulative_stress": agent.cumulative_stress,
        "last_simulation_date": agent.last_simulation_date,
        "updated_at": datetime.utcnow().isoformat(),
    }


def _normalize_loaded_state(record: Dict[str, Any]) -> Dict[str, Any]:
    """Map a Supabase row into the profile state keys used by OPS."""
    return {
        "simulation_history": list(record.get("simulation_history") or []),
        "baseline_anxiety": float(record.get("baseline_anxiety", 5.0) or 5.0),
        "current_trust_government": record.get("current_trust_government"),
        "current_shame_sensitivity": record.get("current_shame_sensitivity"),
        "cumulative_stress": float(record.get("cumulative_stress", 0.0) or 0.0),
        "last_simulation_date": record.get("last_simulation_date"),
    }


def _save_agent_state_sync(agent, project_id: str) -> None:
    client = _get_client()
    if client is None:
        return

    payload = _build_agent_state_payload(agent, project_id)
    client.table("ops_agent_states").upsert(
        payload,
        on_conflict="agent_user_id,project_id",
    ).execute()


def _load_agent_state_sync(user_id: int, project_id: str) -> Optional[Dict[str, Any]]:
    client = _get_client()
    if client is None:
        return None

    result = (
        client.table("ops_agent_states")
        .select("*")
        .eq("agent_user_id", user_id)
        .eq("project_id", project_id)
        .limit(1)
        .execute()
    )
    rows = getattr(result, "data", None) or []
    if not rows:
        return None
    return _normalize_loaded_state(rows[0])


async def save_agent_state(agent, project_id: str) -> None:
    """Upsert one OPS agent's temporal state into Supabase."""
    await asyncio.to_thread(_save_agent_state_sync, agent, project_id)


async def load_agent_state(user_id: int, project_id: str) -> Optional[Dict]:
    """Load one OPS agent's temporal state from Supabase."""
    return await asyncio.to_thread(_load_agent_state_sync, user_id, project_id)


async def load_agent_states(user_ids: List[int], project_id: str) -> Dict[int, Dict[str, Any]]:
    """Load multiple OPS agent states in parallel for a single project."""
    tasks = [load_agent_state(user_id, project_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks)
    state_map: Dict[int, Dict[str, Any]] = {}
    for user_id, state in zip(user_ids, results):
        if state:
            state_map[user_id] = state
    return state_map
