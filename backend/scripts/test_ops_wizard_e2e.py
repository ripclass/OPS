"""
End-to-end tests for the OPS wizard flow in prepare_simulation().

Test 1: Structured params path (ops_population_params dict)
Test 2: Metadata text path ([OPS Wizard Metadata] block)
Test 3: MiroFish fallback (no OPS params at all)
"""

import json
import os
import sys
import shutil
import tempfile
import types
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, backend_dir)

# ---------------------------------------------------------------------------
# Stub ALL heavy transitive imports before touching app.services.
# Uses a "catch-all" module class so any attribute lookup returns a stub.
# ---------------------------------------------------------------------------

class _StubModule(types.ModuleType):
    """Module stub that returns a dummy for any attribute access."""
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        # Return a callable class-like stub
        return type(name, (), {"__init__": lambda self, *a, **kw: None})

_STUB_PREFIXES = [
    "zep_cloud", "camel", "supabase", "fitz",
    "readability", "bs4", "lxml",
]

class _StubImportHook:
    """Meta-path finder that intercepts imports matching our stub prefixes."""
    def find_module(self, fullname, path=None):
        for prefix in _STUB_PREFIXES:
            if fullname == prefix or fullname.startswith(prefix + "."):
                return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = _StubModule(fullname)
        mod.__path__ = []  # Allow sub-imports
        mod.__loader__ = self
        sys.modules[fullname] = mod
        return mod

# Install the hook AND pre-populate known sub-modules to avoid any ordering issues
_hook = _StubImportHook()
sys.meta_path.insert(0, _hook)

# Pre-populate common sub-modules that are imported via `from X import Y`
_pre_stubs = [
    "zep_cloud", "zep_cloud.client", "zep_cloud.types",
    "camel", "camel.oasis",
    "supabase",
    "fitz",
    "readability", "readability.readability",
    "bs4", "lxml", "lxml.html",
]
for mod_name in _pre_stubs:
    _hook.load_module(mod_name)

# Now import what we need — transitive deps are stubbed
from app.services.simulation_manager import SimulationManager, SimulationState, SimulationStatus
from app.services.ops_population_generator import OPSPopulationGenerator, normalize_ops_population_params
from app.services.oasis_profile_generator import OasisAgentProfile, OasisProfileGenerator
from app.services.zep_entity_reader import EntityNode, FilteredEntities
from app.services.simulation_config_generator import SimulationParameters


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_dummy_filtered_entities(count=5):
    """Create a FilteredEntities with dummy EntityNode objects for the MiroFish path."""
    entities = []
    for i in range(count):
        entities.append(EntityNode(
            uuid=f"zep_entity_{i}",
            name=f"Test Entity {i}",
            labels=["Person", "Entity"],
            summary=f"Test entity {i} is a community member involved in public discussion.",
            attributes={"type": "Person"},
        ))
    return FilteredEntities(
        entities=entities,
        entity_types={"Person"},
        total_count=count,
        filtered_count=count,
    )


def make_mock_sim_params(simulation_id, project_id, graph_id):
    """Create a minimal SimulationParameters for config generation mocking."""
    return SimulationParameters(
        simulation_id=simulation_id,
        project_id=project_id,
        graph_id=graph_id,
        simulation_requirement="test requirement",
        generation_reasoning="Mocked config generation",
    )


def print_profile_summary(profile: OasisAgentProfile, index: int):
    """Print a concise agent profile summary."""
    print(f"  Agent #{index}:")
    print(f"    Name:             {profile.name}")
    print(f"    Segment:          {profile.source_entity_type}")
    print(f"    Country:          {profile.country}")
    print(f"    Location:         {profile.location}")
    print(f"    Profession:       {profile.profession}")
    print(f"    Age/Gender:       {profile.age} / {profile.gender}")
    print(f"    Trust Gov:        {profile.trust_government}")
    print(f"    Shame Sens:       {profile.shame_sensitivity}")
    print(f"    Primary Fear:     {profile.primary_fear}")
    print(f"    Dialect:          {profile.dialect}")
    print(f"    FB Intensity:     {profile.fb_intensity}")
    print(f"    Influence Radius: {profile.influence_radius}")
    print(f"    Bio:              {profile.bio[:100]}...")
    print()


# ---------------------------------------------------------------------------
# Shared patching context — mocks external services but lets OPS generator run
# ---------------------------------------------------------------------------

def run_prepare_simulation(manager, simulation_id, simulation_requirement, ops_profiles_holder=None):
    """Run prepare_simulation with all external dependencies mocked."""

    dummy_filtered = make_dummy_filtered_entities(5)
    state = manager._load_simulation_state(simulation_id)

    with patch.object(
        manager, "_hydrate_profiles_from_memory", side_effect=lambda profiles, pid: profiles
    ), patch(
        "app.services.simulation_manager.ZepEntityReader"
    ) as MockZepReader, patch(
        "app.services.simulation_manager.SimulationConfigGenerator"
    ) as MockConfigGen:

        # ZepEntityReader mock
        mock_reader_instance = MagicMock()
        mock_reader_instance.filter_defined_entities.return_value = dummy_filtered
        MockZepReader.return_value = mock_reader_instance

        # SimulationConfigGenerator mock
        mock_config_instance = MagicMock()
        mock_config_instance.generate_config.return_value = make_mock_sim_params(
            simulation_id, state.project_id, state.graph_id
        )
        MockConfigGen.return_value = mock_config_instance

        # OasisProfileGenerator — patch save methods only, let profile generation run
        with patch.object(OasisProfileGenerator, "save_profiles"), \
             patch.object(OasisProfileGenerator, "save_profiles_snapshot"):

            result = manager.prepare_simulation(
                simulation_id=simulation_id,
                simulation_requirement=simulation_requirement,
                document_text="Test document for OPS wizard e2e.",
                use_llm_for_profiles=False,  # Use rule-based fallback, no LLM needed
            )

        return result, mock_reader_instance


# ===========================================================================
# TEST 1 — Structured params path
# ===========================================================================

def test_1_structured_params():
    print("=" * 70)
    print("TEST 1: Structured params path (ops_population_params dict)")
    print("=" * 70)

    ops_params = {
        "run_type": "Domestic",
        "origin_country": "Bangladesh",
        "segments": ["rural", "urban working class"],
        "n_agents": 100,
        "region": "mixed",
    }

    tmp_dir = tempfile.mkdtemp(prefix="ops_test1_")
    try:
        manager = SimulationManager()
        manager.SIMULATION_DATA_DIR = tmp_dir

        # Create a simulation with OPS params
        state = manager.create_simulation(
            project_id="test_project_1",
            graph_id="test_graph_1",
            ops_population_params=ops_params,
        )
        sim_id = state.simulation_id

        # Verify params were normalized and stored
        assert state.ops_population_params is not None, "ops_population_params should be set"
        assert "rural" in state.ops_population_params["segments"], "Should contain 'rural' segment"
        assert "urban_working" in state.ops_population_params["segments"], "Should contain 'urban_working' segment"
        print(f"  [OK] Simulation created: {sim_id}")
        print(f"  [OK] Normalized params: segments={state.ops_population_params['segments']}, n_agents={state.ops_population_params['n_agents']}")

        # Patch OPSPopulationGenerator to spy on it
        original_generate = OPSPopulationGenerator.generate_population
        ops_gen_called = False
        generated_profiles = []

        def spy_generate(self_gen, params, scenario_context, use_llm=True):
            nonlocal ops_gen_called, generated_profiles
            ops_gen_called = True
            result = original_generate(self_gen, params, scenario_context, use_llm=use_llm)
            generated_profiles.extend(result)
            return result

        with patch.object(OPSPopulationGenerator, "generate_population", spy_generate):
            result_state, mock_reader = run_prepare_simulation(
                manager, sim_id, "Test scenario: price shock affecting Bangladesh rural and urban populations."
            )

        # Assertions
        assert ops_gen_called, "OPSPopulationGenerator.generate_population should have been called"
        print(f"  [OK] OPSPopulationGenerator was called (NOT MiroFish)")

        assert result_state.status == SimulationStatus.READY, f"Expected READY, got {result_state.status}"
        print(f"  [OK] Simulation status: {result_state.status.value}")

        assert len(generated_profiles) > 0, "Should have generated profiles"
        print(f"  [OK] Generated {len(generated_profiles)} agent profiles")

        assert result_state.profiles_count == len(generated_profiles)
        print(f"  [OK] State.profiles_count = {result_state.profiles_count}")

        # Print first 3 agent profiles
        print()
        print("  --- First 3 Agent Profiles ---")
        for i, profile in enumerate(generated_profiles[:3]):
            print_profile_summary(profile, i)

        print("  >>> TEST 1: PASS")
        return True, generated_profiles

    except Exception as e:
        print(f"  >>> TEST 1: FAIL — {e}")
        import traceback
        traceback.print_exc()
        return False, []
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ===========================================================================
# TEST 2 — Metadata text path
# ===========================================================================

def test_2_metadata_text():
    print()
    print("=" * 70)
    print("TEST 2: Metadata text path ([OPS Wizard Metadata] block)")
    print("=" * 70)

    simulation_requirement = """Simulate public opinion dynamics in rural Pakistan.

[OPS Wizard Metadata]
Run Type: Domestic
Origin Country: Pakistan
Segments: rural, middle class, students
Target Agents: 50
Region: mixed
Requested Outputs: reddit, twitter
[/OPS Wizard Metadata]

Focus on how price shocks affect rural communities and student populations."""

    tmp_dir = tempfile.mkdtemp(prefix="ops_test2_")
    try:
        manager = SimulationManager()
        manager.SIMULATION_DATA_DIR = tmp_dir

        # Create simulation WITHOUT ops_population_params
        state = manager.create_simulation(
            project_id="test_project_2",
            graph_id="test_graph_2",
            ops_population_params=None,  # No structured params
        )
        sim_id = state.simulation_id

        assert state.ops_population_params is None, "ops_population_params should be None initially"
        print(f"  [OK] Simulation created with NO ops_population_params: {sim_id}")

        # Test the parser directly first
        parsed = SimulationManager._parse_ops_wizard_metadata(simulation_requirement)
        assert parsed is not None, "Parser should extract metadata block"
        print(f"  [OK] Parser extracted raw metadata:")
        print(f"       run_type:       {parsed.get('run_type')}")
        print(f"       origin_country: {parsed.get('origin_country')}")
        print(f"       segments:       {parsed.get('segments')}")
        print(f"       n_agents:       {parsed.get('n_agents')}")
        print(f"       region:         {parsed.get('region')}")

        normalized = normalize_ops_population_params(parsed)
        assert normalized is not None, "Normalized params should not be None"
        print(f"  [OK] Normalized params dict:")
        for k, v in normalized.items():
            print(f"       {k}: {v}")

        assert normalized["origin_country"] == "Pakistan"
        assert "rural" in normalized["segments"]
        assert "middle_class" in normalized["segments"]
        assert "students" in normalized["segments"]
        assert normalized["n_agents"] == 50

        # Now run the full prepare_simulation and verify OPS generator is called
        ops_gen_called = False
        original_generate = OPSPopulationGenerator.generate_population

        def spy_generate(self_gen, params, scenario_context, use_llm=True):
            nonlocal ops_gen_called
            ops_gen_called = True
            return original_generate(self_gen, params, scenario_context, use_llm=use_llm)

        with patch.object(OPSPopulationGenerator, "generate_population", spy_generate):
            result_state, _ = run_prepare_simulation(manager, sim_id, simulation_requirement)

        assert ops_gen_called, "OPSPopulationGenerator should have been called via metadata path"
        print(f"  [OK] OPSPopulationGenerator was called (metadata text path)")

        assert result_state.status == SimulationStatus.READY
        print(f"  [OK] Simulation status: {result_state.status.value}")

        assert result_state.ops_population_params is not None
        print(f"  [OK] State.ops_population_params was populated from metadata block")
        print(f"  [OK] Generated {result_state.profiles_count} profiles")

        print()
        print("  >>> TEST 2: PASS")
        return True

    except Exception as e:
        print(f"  >>> TEST 2: FAIL — {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ===========================================================================
# TEST 3 — MiroFish fallback
# ===========================================================================

def test_3_mirofish_fallback():
    print()
    print("=" * 70)
    print("TEST 3: MiroFish fallback (no OPS params, no metadata block)")
    print("=" * 70)

    simulation_requirement = "Simulate general public discussion about economic changes. No special population parameters."

    tmp_dir = tempfile.mkdtemp(prefix="ops_test3_")
    try:
        manager = SimulationManager()
        manager.SIMULATION_DATA_DIR = tmp_dir

        # Create simulation without OPS params
        state = manager.create_simulation(
            project_id="test_project_3",
            graph_id="test_graph_3",
            ops_population_params=None,
        )
        sim_id = state.simulation_id

        assert state.ops_population_params is None
        print(f"  [OK] Simulation created with NO ops_population_params: {sim_id}")

        # Verify parser returns None for this requirement
        parsed = SimulationManager._parse_ops_wizard_metadata(simulation_requirement)
        assert parsed is None, "Parser should return None (no metadata block)"
        print(f"  [OK] Parser correctly returned None (no metadata block)")

        # Track whether OPSPopulationGenerator is called (it should NOT be)
        ops_gen_called = False
        original_generate = OPSPopulationGenerator.generate_population

        def spy_generate(self_gen, params, scenario_context, use_llm=True):
            nonlocal ops_gen_called
            ops_gen_called = True
            return original_generate(self_gen, params, scenario_context, use_llm=use_llm)

        # Track whether MiroFish path (generate_profiles_from_entities) is called
        mirofish_called = False
        original_mirofish = OasisProfileGenerator.generate_profiles_from_entities

        def spy_mirofish(self_gen, *args, **kwargs):
            nonlocal mirofish_called
            mirofish_called = True
            return original_mirofish(self_gen, *args, **kwargs)

        with patch.object(OPSPopulationGenerator, "generate_population", spy_generate), \
             patch.object(OasisProfileGenerator, "generate_profiles_from_entities", spy_mirofish):
            result_state, _ = run_prepare_simulation(manager, sim_id, simulation_requirement)

        assert not ops_gen_called, "OPSPopulationGenerator should NOT have been called"
        print(f"  [OK] OPSPopulationGenerator was NOT called")

        assert mirofish_called, "MiroFish entity pipeline (generate_profiles_from_entities) should have been called"
        print(f"  [OK] MiroFish entity pipeline WAS called")

        assert result_state.status == SimulationStatus.READY
        print(f"  [OK] Simulation status: {result_state.status.value}")
        print(f"  [OK] No errors thrown")
        print(f"  [OK] Generated {result_state.profiles_count} profiles via MiroFish fallback")

        print()
        print("  >>> TEST 3: PASS")
        return True

    except Exception as e:
        print(f"  >>> TEST 3: FAIL — {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print()
    print("OPS Wizard Flow — End-to-End Tests")
    print("=" * 70)
    print()

    pass1, profiles = test_1_structured_params()
    pass2 = test_2_metadata_text()
    pass3 = test_3_mirofish_fallback()

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Test 1 (Structured params):  {'PASS' if pass1 else 'FAIL'}")
    print(f"  Test 2 (Metadata text):      {'PASS' if pass2 else 'FAIL'}")
    print(f"  Test 3 (MiroFish fallback):  {'PASS' if pass3 else 'FAIL'}")
    print()

    if pass1 and profiles:
        print("=" * 70)
        print("AGENT PROFILES FROM TEST 1 (first 3)")
        print("=" * 70)
        for i, p in enumerate(profiles[:3]):
            print_profile_summary(p, i)

    all_passed = pass1 and pass2 and pass3
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_passed else 1)
