"""
Intelligent simulation configuration generator.
Uses the LLM to automatically generate detailed simulation parameters from the simulation requirements, document content, and graph information.
Supports a fully automated flow with no manual parameter setup.

It uses a step-by-step generation strategy to avoid failures caused by generating too much content at once:
1. Generate the time configuration
2. Generate the event configuration
3. Generate agent configurations in batches
4. Generate the platform configuration
"""

import json
import math
import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime

from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger
from .zep_entity_reader import EntityNode, ZepEntityReader

logger = get_logger('ops.simulation_config')

# Time-of-day configuration aligned with a regional daily schedule
REGIONAL_TIME_CONFIG = {
    # Late-night hours with almost no activity
    "dead_hours": [0, 1, 2, 3, 4, 5],
    # Morning hours when activity gradually starts
    "morning_hours": [6, 7, 8],
    # Working hours
    "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    # Evening peak hours with the highest activity
    "peak_hours": [19, 20, 21, 22],
    # Night hours when activity declines
    "night_hours": [23],
    # Activity multipliers
    "activity_multipliers": {
        "dead": 0.05,      # Almost nobody is active overnight
        "morning": 0.4,    # Activity ramps up in the morning
        "work": 0.7,       # Moderate activity during working hours
        "peak": 1.5,       # Evening peak
        "night": 0.5       # Activity falls off late at night
    }
}


@dataclass
class AgentActivityConfig:
    """Activity configuration for a single agent."""
    agent_id: int
    entity_uuid: str
    entity_name: str
    entity_type: str
    
    # Activity level (0.0-1.0)
    activity_level: float = 0.5  # Overall activity level
    
    # Speaking frequency (expected number of posts per hour)
    posts_per_hour: float = 1.0
    comments_per_hour: float = 2.0
    
    # Active hours (24-hour clock, 0-23)
    active_hours: List[int] = field(default_factory=lambda: list(range(8, 23)))
    
    # Response speed (reaction delay to hot events, measured in simulated minutes)
    response_delay_min: int = 5
    response_delay_max: int = 60
    
    # Sentiment bias (-1.0 to 1.0, from negative to positive)
    sentiment_bias: float = 0.0
    
    # Stance toward specific topics
    stance: str = "neutral"  # supportive, opposing, neutral, observer
    
    # Influence weight (how likely other agents are to see this agent's posts)
    influence_weight: float = 1.0


@dataclass  
class TimeSimulationConfig:
    """Time simulation configuration based on a regional daily schedule."""
    # Total simulation duration in simulated hours
    total_simulation_hours: int = 72  # Default: simulate 72 hours (3 days)
    
    # Time represented by each round in simulated minutes. Default: 60 minutes (1 hour) to speed up time flow.
    minutes_per_round: int = 60
    
    # Range of agents activated per hour
    agents_per_hour_min: int = 5
    agents_per_hour_max: int = 20
    
    # Peak hours (19:00-22:00 in the evening, when activity is highest)
    peak_hours: List[int] = field(default_factory=lambda: [19, 20, 21, 22])
    peak_activity_multiplier: float = 1.5
    
    # Off-peak hours (00:00-05:00, when activity is very low)
    off_peak_hours: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    off_peak_activity_multiplier: float = 0.05  # Very low activity overnight
    
    # Morning hours
    morning_hours: List[int] = field(default_factory=lambda: [6, 7, 8])
    morning_activity_multiplier: float = 0.4
    
    # Working hours
    work_hours: List[int] = field(default_factory=lambda: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    work_activity_multiplier: float = 0.7


@dataclass
class EventConfig:
    """Event configuration."""
    # Initial events that trigger the simulation at the start
    initial_posts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scheduled events that are triggered at specific times
    scheduled_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Hot-topic keywords
    hot_topics: List[str] = field(default_factory=list)
    
    # Narrative direction
    narrative_direction: str = ""


@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    platform: str  # twitter or reddit
    
    # Recommendation algorithm weights
    recency_weight: float = 0.4  # Recency
    popularity_weight: float = 0.3  # Popularity
    relevance_weight: float = 0.3  # Relevance
    
    # Viral spread threshold: number of interactions required before amplification
    viral_threshold: int = 10
    
    # Echo-chamber strength: how strongly similar viewpoints cluster together
    echo_chamber_strength: float = 0.5


@dataclass
class SimulationParameters:
    """Full simulation parameter configuration."""
    # Basic information
    simulation_id: str
    project_id: str
    graph_id: str
    simulation_requirement: str
    
    # Time configuration
    time_config: TimeSimulationConfig = field(default_factory=TimeSimulationConfig)
    
    # Agent configuration list
    agent_configs: List[AgentActivityConfig] = field(default_factory=list)
    
    # Event configuration
    event_config: EventConfig = field(default_factory=EventConfig)
    
    # Platform configuration
    twitter_config: Optional[PlatformConfig] = None
    reddit_config: Optional[PlatformConfig] = None
    
    # LLM configuration
    llm_model: str = ""
    llm_base_url: str = ""
    
    # Generation metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    generation_reasoning: str = ""  # LLM reasoning notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        time_dict = asdict(self.time_config)
        return {
            "simulation_id": self.simulation_id,
            "project_id": self.project_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "time_config": time_dict,
            "agent_configs": [asdict(a) for a in self.agent_configs],
            "event_config": asdict(self.event_config),
            "twitter_config": asdict(self.twitter_config) if self.twitter_config else None,
            "reddit_config": asdict(self.reddit_config) if self.reddit_config else None,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url,
            "generated_at": self.generated_at,
            "generation_reasoning": self.generation_reasoning,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class SimulationConfigGenerator:
    """
    Intelligent simulation configuration generator.

    Uses the LLM to analyze the simulation requirements, document content, and graph entity information,
    then automatically generates an optimized simulation configuration.

    Step-by-step generation strategy:
    1. Generate the time and event configurations first (lightweight)
    2. Generate agent configurations in batches of roughly 10-20
    3. Generate the platform configuration
    """
    
    # Maximum context length in characters
    MAX_CONTEXT_LENGTH = 50000
    # Number of agents generated per batch
    AGENTS_PER_BATCH = 15
    
    # Context truncation length for each step, in characters
    TIME_CONFIG_CONTEXT_LENGTH = 10000   # Time configuration
    EVENT_CONFIG_CONTEXT_LENGTH = 8000   # Event configuration
    ENTITY_SUMMARY_LENGTH = 300          # Entity summary
    AGENT_SUMMARY_LENGTH = 300           # Entity summary used during agent configuration
    ENTITIES_PER_TYPE_DISPLAY = 20       # Number of entities displayed per type
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_config(
        self,
        simulation_id: str,
        project_id: str,
        graph_id: str,
        simulation_requirement: str,
        document_text: str,
        entities: List[EntityNode],
        context_entities: Optional[List[EntityNode]] = None,
        enable_twitter: bool = True,
        enable_reddit: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> SimulationParameters:
        """
        Intelligently generate the full simulation configuration in multiple steps.
        
        Args:
            simulation_id: Simulation ID
            project_id: Project ID
            graph_id: Graph ID
            simulation_requirement: Simulation requirement description
            document_text: Original document content
            entities: Agent entities used to size and configure the simulated population
            context_entities: Optional graph entities used to build scenario context
            enable_twitter: Whether to enable Twitter
            enable_reddit: Whether to enable Reddit
            progress_callback: Progress callback function `(current_step, total_steps, message)`
            
        Returns:
            SimulationParameters: Full simulation parameters
        """
        context_entities = context_entities or entities
        logger.info(
            f"Starting intelligent simulation config generation: simulation_id={simulation_id}, "
            f"agent_entity_count={len(entities)}, context_entity_count={len(context_entities)}"
        )
        
        # Compute the total number of steps
        num_batches = math.ceil(len(entities) / self.AGENTS_PER_BATCH)
        total_steps = 3 + num_batches  # Time config + event config + N agent batches + platform config
        current_step = 0
        
        def report_progress(step: int, message: str):
            nonlocal current_step
            current_step = step
            if progress_callback:
                progress_callback(step, total_steps, message)
            logger.info(f"[{step}/{total_steps}] {message}")
        
        # 1. Build the base context
        context = self._build_context(
            simulation_requirement=simulation_requirement,
            document_text=document_text,
            entities=context_entities
        )
        
        reasoning_parts = []
        
        # ========== Step 1: Generate the time configuration ==========
        report_progress(1, "Generating the time configuration...")
        num_entities = len(entities)
        time_config_result = self._generate_time_config(context, num_entities)
        time_config = self._parse_time_config(time_config_result, num_entities)
        reasoning_parts.append(f"Time configuration: {time_config_result.get('reasoning', 'success')}")
        
        # ========== Step 2: Generate the event configuration ==========
        report_progress(2, "Generating the event configuration and hot topics...")
        event_config_result = self._generate_event_config(context, simulation_requirement, entities)
        event_config = self._parse_event_config(event_config_result)
        reasoning_parts.append(f"Event configuration: {event_config_result.get('reasoning', 'success')}")
        
        # ========== Step 3-N: Generate agent configurations in batches ==========
        all_agent_configs = []
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.AGENTS_PER_BATCH
            end_idx = min(start_idx + self.AGENTS_PER_BATCH, len(entities))
            batch_entities = entities[start_idx:end_idx]
            
            report_progress(
                3 + batch_idx,
                f"Generating agent configuration ({start_idx + 1}-{end_idx}/{len(entities)})..."
            )
            
            batch_configs = self._generate_agent_configs_batch(
                context=context,
                entities=batch_entities,
                start_idx=start_idx,
                simulation_requirement=simulation_requirement
            )
            all_agent_configs.extend(batch_configs)
        
        reasoning_parts.append(f"Agent configuration: generated {len(all_agent_configs)} successfully")
        
        # ========== Assign agent authors to initial posts ==========
        logger.info("Assigning suitable agent authors to the initial posts...")
        event_config = self._assign_initial_post_agents(event_config, all_agent_configs)
        assigned_count = len([p for p in event_config.initial_posts if p.get("poster_agent_id") is not None])
        reasoning_parts.append(f"Initial post assignment: assigned authors to {assigned_count} posts")
        
        # ========== Final step: generate the platform configuration ==========
        report_progress(total_steps, "Generating the platform configuration...")
        twitter_config = None
        reddit_config = None
        
        if enable_twitter:
            twitter_config = PlatformConfig(
                platform="twitter",
                recency_weight=0.4,
                popularity_weight=0.3,
                relevance_weight=0.3,
                viral_threshold=10,
                echo_chamber_strength=0.5
            )
        
        if enable_reddit:
            reddit_config = PlatformConfig(
                platform="reddit",
                recency_weight=0.3,
                popularity_weight=0.4,
                relevance_weight=0.3,
                viral_threshold=15,
                echo_chamber_strength=0.6
            )
        
        # Build the final parameters
        params = SimulationParameters(
            simulation_id=simulation_id,
            project_id=project_id,
            graph_id=graph_id,
            simulation_requirement=simulation_requirement,
            time_config=time_config,
            agent_configs=all_agent_configs,
            event_config=event_config,
            twitter_config=twitter_config,
            reddit_config=reddit_config,
            llm_model=self.model_name,
            llm_base_url=self.base_url,
            generation_reasoning=" | ".join(reasoning_parts)
        )
        
        logger.info(f"Simulation configuration generation complete: {len(params.agent_configs)} agent configs")
        
        return params
    
    def _build_context(
        self,
        simulation_requirement: str,
        document_text: str,
        entities: List[EntityNode]
    ) -> str:
        """Build the LLM context and truncate it to the maximum length."""
        
        # Entity summary
        entity_summary = self._summarize_entities(entities)
        
        # Build the context
        context_parts = [
            f"## Simulation Requirement\n{simulation_requirement}",
            f"\n## Entity Information ({len(entities)})\n{entity_summary}",
        ]
        
        current_length = sum(len(p) for p in context_parts)
        remaining_length = self.MAX_CONTEXT_LENGTH - current_length - 500  # Keep a 500-character buffer
        
        if remaining_length > 0 and document_text:
            doc_text = document_text[:remaining_length]
            if len(document_text) > remaining_length:
                doc_text += "\n...(document truncated)"
            context_parts.append(f"\n## Original Document Content\n{doc_text}")
        
        return "\n".join(context_parts)
    
    def _summarize_entities(self, entities: List[EntityNode]) -> str:
        """Generate the entity summary."""
        lines = []
        
        # Group by type
        by_type: Dict[str, List[EntityNode]] = {}
        for e in entities:
            t = e.get_entity_type() or "Unknown"
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(e)
        
        for entity_type, type_entities in by_type.items():
            lines.append(f"\n### {entity_type} ({len(type_entities)})")
            # Use the configured display count and summary length
            display_count = self.ENTITIES_PER_TYPE_DISPLAY
            summary_len = self.ENTITY_SUMMARY_LENGTH
            for e in type_entities[:display_count]:
                summary_preview = (e.summary[:summary_len] + "...") if len(e.summary) > summary_len else e.summary
                lines.append(f"- {e.name}: {summary_preview}")
            if len(type_entities) > display_count:
                lines.append(f"  ... and {len(type_entities) - display_count} more")
        
        return "\n".join(lines)
    
    def _call_llm_with_retry(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """LLM call with retry logic, including JSON repair."""
        import re
        
        max_attempts = 3
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7 - (attempt * 0.1)  # Lower the temperature on each retry
                    # Do not set `max_tokens`; allow the LLM to respond freely
                )
                
                content = response.choices[0].message.content
                finish_reason = response.choices[0].finish_reason
                
                # Check whether the output was truncated
                if finish_reason == 'length':
                    logger.warning(f"LLM output was truncated (attempt {attempt+1})")
                    content = self._fix_truncated_json(content)
                
                # Try to parse the JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed (attempt {attempt+1}): {str(e)[:80]}")
                    
                    # Attempt to repair the JSON
                    fixed = self._try_fix_config_json(content)
                    if fixed:
                        return fixed
                    
                    last_error = e
                    
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt+1}): {str(e)[:80]}")
                last_error = e
                import time
                time.sleep(2 * (attempt + 1))
        
        raise last_error or Exception("LLM call failed")
    
    def _fix_truncated_json(self, content: str) -> str:
        """Repair truncated JSON."""
        content = content.strip()
        
        # Count unclosed brackets and braces
        open_braces = content.count('{') - content.count('}')
        open_brackets = content.count('[') - content.count(']')
        
        # Check for an unclosed string
        if content and content[-1] not in '",}]':
            content += '"'
        
        # Close brackets and braces
        content += ']' * open_brackets
        content += '}' * open_braces
        
        return content
    
    def _try_fix_config_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair configuration JSON."""
        import re
        
        # Repair truncation
        content = self._fix_truncated_json(content)
        
        # Extract the JSON portion
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            
            # Remove newline characters inside strings
            def fix_string(match):
                s = match.group(0)
                s = s.replace('\n', ' ').replace('\r', ' ')
                s = re.sub(r'\s+', ' ', s)
                return s
            
            json_str = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', fix_string, json_str)
            
            try:
                return json.loads(json_str)
            except:
                # Try removing all control characters
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
                json_str = re.sub(r'\s+', ' ', json_str)
                try:
                    return json.loads(json_str)
                except:
                    pass
        
        return None
    
    def _generate_time_config(self, context: str, num_entities: int) -> Dict[str, Any]:
        """Generate the time configuration."""
        # Use the configured context truncation length
        context_truncated = context[:self.TIME_CONFIG_CONTEXT_LENGTH]
        
        # Compute the maximum allowed value (90% of the agent count)
        max_agents_allowed = max(1, int(num_entities * 0.9))
        
        prompt = f"""Generate a time simulation configuration based on the following simulation context.

{context_truncated}

## Task
Generate the time configuration as JSON.

### General principles (reference only; adapt them to the specific event and participant group):
- The user population follows a region-aware daily schedule aligned with local time
- Activity is extremely low from 00:00 to 05:00 (activity multiplier 0.05)
- Activity gradually rises from 06:00 to 08:00 (activity multiplier 0.4)
- Activity is moderate during working hours from 09:00 to 18:00 (activity multiplier 0.7)
- The evening peak is 19:00 to 22:00 (activity multiplier 1.5)
- Activity declines after 23:00 (activity multiplier 0.5)
- General pattern: very low overnight, gradually rising in the morning, moderate during work hours, peak in the evening
- **Important**: the example values below are only references. Adjust the exact time ranges based on the nature of the event and the participant groups.
  - Example: student groups may peak at 21:00-23:00; media may be active all day; official institutions may act only during working hours
  - Example: sudden breaking events may still produce discussion late at night, so `off_peak_hours` may need to be shortened

### Return JSON only (no Markdown)

Example:
{{
    "total_simulation_hours": 72,
    "minutes_per_round": 60,
    "agents_per_hour_min": 5,
    "agents_per_hour_max": 50,
    "peak_hours": [19, 20, 21, 22],
    "off_peak_hours": [0, 1, 2, 3, 4, 5],
    "morning_hours": [6, 7, 8],
    "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "reasoning": "Explanation of the time configuration chosen for this event"
}}

Field definitions:
- total_simulation_hours (int): total simulation length, 24-168 hours; shorter for breaking events, longer for persistent topics
- minutes_per_round (int): duration of each round, 30-120 minutes; 60 minutes is recommended
- agents_per_hour_min (int): minimum number of active agents per hour (range: 1-{max_agents_allowed})
- agents_per_hour_max (int): maximum number of active agents per hour (range: 1-{max_agents_allowed})
- peak_hours (array[int]): peak periods, adjusted for the event's participant group
- off_peak_hours (array[int]): off-peak periods, usually overnight
- morning_hours (array[int]): morning period
- work_hours (array[int]): working period
- reasoning (string): brief explanation of why this configuration was chosen"""

        system_prompt = "You are a social media simulation expert. Return pure JSON only. The time configuration must follow a realistic regional daily schedule."
        
        try:
            return self._call_llm_with_retry(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"Time configuration generation by the LLM failed: {e}. Using the default configuration instead.")
            return self._get_default_time_config(num_entities)
    
    def _get_default_time_config(self, num_entities: int) -> Dict[str, Any]:
        """Get the default time configuration based on a regional daily schedule."""
        return {
            "total_simulation_hours": 72,
            "minutes_per_round": 60,  # One hour per round to speed up the simulated timeline
            "agents_per_hour_min": max(1, num_entities // 15),
            "agents_per_hour_max": max(5, num_entities // 5),
            "peak_hours": [19, 20, 21, 22],
            "off_peak_hours": [0, 1, 2, 3, 4, 5],
            "morning_hours": [6, 7, 8],
            "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "reasoning": "Using the default regional schedule configuration with one hour per round"
        }
    
    def _parse_time_config(self, result: Dict[str, Any], num_entities: int) -> TimeSimulationConfig:
        """Parse the time configuration result and ensure `agents_per_hour` does not exceed the total number of agents."""
        # Get the raw values
        agents_per_hour_min = result.get("agents_per_hour_min", max(1, num_entities // 15))
        agents_per_hour_max = result.get("agents_per_hour_max", max(5, num_entities // 5))
        
        # Validate and correct values so they do not exceed the total number of agents
        if agents_per_hour_min > num_entities:
            logger.warning(f"agents_per_hour_min ({agents_per_hour_min}) exceeded the total agent count ({num_entities}) and was corrected")
            agents_per_hour_min = max(1, num_entities // 10)
        
        if agents_per_hour_max > num_entities:
            logger.warning(f"agents_per_hour_max ({agents_per_hour_max}) exceeded the total agent count ({num_entities}) and was corrected")
            agents_per_hour_max = max(agents_per_hour_min + 1, num_entities // 2)
        
        # Ensure `min < max`
        if agents_per_hour_min >= agents_per_hour_max:
            agents_per_hour_min = max(1, agents_per_hour_max // 2)
            logger.warning(f"agents_per_hour_min was greater than or equal to max and was corrected to {agents_per_hour_min}")
        
        return TimeSimulationConfig(
            total_simulation_hours=result.get("total_simulation_hours", 72),
            minutes_per_round=result.get("minutes_per_round", 60),  # Default to one hour per round
            agents_per_hour_min=agents_per_hour_min,
            agents_per_hour_max=agents_per_hour_max,
            peak_hours=result.get("peak_hours", [19, 20, 21, 22]),
            off_peak_hours=result.get("off_peak_hours", [0, 1, 2, 3, 4, 5]),
            off_peak_activity_multiplier=0.05,  # Almost nobody is active overnight
            morning_hours=result.get("morning_hours", [6, 7, 8]),
            morning_activity_multiplier=0.4,
            work_hours=result.get("work_hours", list(range(9, 19))),
            work_activity_multiplier=0.7,
            peak_activity_multiplier=1.5
        )
    
    def _generate_event_config(
        self, 
        context: str, 
        simulation_requirement: str,
        entities: List[EntityNode]
    ) -> Dict[str, Any]:
        """Generate the event configuration."""
        
        # Gather the available entity types for LLM reference
        entity_types_available = list(set(
            e.get_entity_type() or "Unknown" for e in entities
        ))
        
        # List representative entity names for each type
        type_examples = {}
        for e in entities:
            etype = e.get_entity_type() or "Unknown"
            if etype not in type_examples:
                type_examples[etype] = []
            if len(type_examples[etype]) < 3:
                type_examples[etype].append(e.name)
        
        type_info = "\n".join([
            f"- {t}: {', '.join(examples)}" 
            for t, examples in type_examples.items()
        ])
        
        # Use the configured context truncation length
        context_truncated = context[:self.EVENT_CONFIG_CONTEXT_LENGTH]
        
        prompt = f"""Generate the event configuration based on the following simulation requirement.

Simulation requirement: {simulation_requirement}

{context_truncated}

## Available Entity Types and Examples
{type_info}

## Task
Generate the event configuration as JSON:
- extract hot-topic keywords
- describe the narrative direction of the public discourse
- design the initial posts, and **every post must specify a `poster_type`**

**Important**: `poster_type` must be chosen from the available entity types listed above so the initial posts can be assigned to suitable agents.
For example: official statements should come from `Official` or `University`, news should come from `MediaOutlet`, and student perspectives should come from `Student`.
When OPS-specific public archetypes are available, prefer the most specific one instead of generic `Person`.
Examples: `RuralHousehold`, `UrbanWorkingFamily`, `MiddleClassFamily`, `MigrationWorker`, `CorporateProfessional`, `WomenHouseholdVoice`, `ElderlyCitizen`.

Return JSON only (no Markdown):
{{
    "hot_topics": ["keyword1", "keyword2", ...],
    "narrative_direction": "<description of the narrative direction>",
    "initial_posts": [
        {{"content": "post content", "poster_type": "entity type (must be chosen from the available types)"}},
        ...
    ],
    "reasoning": "<brief explanation>"
}}"""

        system_prompt = "You are a public-opinion analysis expert. Return pure JSON only. `poster_type` must exactly match one of the available entity types."
        
        try:
            return self._call_llm_with_retry(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"Event configuration generation by the LLM failed: {e}. Using the default configuration instead.")
            return {
                "hot_topics": [],
                "narrative_direction": "",
                "initial_posts": [],
                "reasoning": "Using the default configuration"
            }
    
    def _parse_event_config(self, result: Dict[str, Any]) -> EventConfig:
        """Parse the event configuration result."""
        return EventConfig(
            initial_posts=result.get("initial_posts", []),
            scheduled_events=[],
            hot_topics=result.get("hot_topics", []),
            narrative_direction=result.get("narrative_direction", "")
        )
    
    def _assign_initial_post_agents(
        self,
        event_config: EventConfig,
        agent_configs: List[AgentActivityConfig]
    ) -> EventConfig:
        """
        Assign suitable author agents to the initial posts.

        Match the most suitable `agent_id` for each post based on its `poster_type`.
        """
        if not event_config.initial_posts:
            return event_config

        def canonicalize_type(value: Any) -> str:
            return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())
        
        # Build an index of agents by entity type
        agents_by_type: Dict[str, List[AgentActivityConfig]] = {}
        for agent in agent_configs:
            etype = canonicalize_type(agent.entity_type)
            if etype not in agents_by_type:
                agents_by_type[etype] = []
            agents_by_type[etype].append(agent)
        
        # Type alias table to handle different formats the LLM may emit
        type_aliases = {
            "official": ["official", "university", "governmentagency", "government"],
            "university": ["university", "official"],
            "mediaoutlet": ["mediaoutlet", "media"],
            "student": ["student", "studentvoice", "youth", "undergraduate", "college", "campusvoice", "person"],
            "professor": ["professor", "expert", "teacher"],
            "alumni": ["alumni", "person"],
            "organization": ["organization", "ngo", "company", "group"],
            "person": ["person", "student", "alumni"],
            "ruralhousehold": ["ruralhousehold", "ruralfamily", "rural", "villagehousehold", "person"],
            "urbanworkingfamily": ["urbanworkingfamily", "urbanworkinghousehold", "urbanworker", "workingclass", "workingfamily", "urbanworking", "person"],
            "middleclassfamily": ["middleclassfamily", "middleclasshousehold", "middleclass", "salariedfamily", "person"],
            "corporateprofessional": ["corporateprofessional", "corporate", "professional", "officeworker", "linkedinprofessional", "person"],
            "migrationworker": ["migrationworker", "migrantworker", "overseasworker", "diasporaworker", "remittancehousehold", "person"],
            "womenhouseholdvoice": ["womenhouseholdvoice", "womenvoice", "householdwoman", "homemaker", "person"],
            "elderlycitizen": ["elderlycitizen", "elderly", "seniorcitizen", "retired", "person"],
        }
        
        # Track which agent index has been used for each type to avoid repeated reuse
        used_indices: Dict[str, int] = {}
        
        updated_posts = []
        for post in event_config.initial_posts:
            poster_type = str(post.get("poster_type", "") or "").lower()
            poster_type_key = canonicalize_type(poster_type)
            content = post.get("content", "")
            
            # Try to find a matching agent
            matched_agent_id = None
            matched_key = None
            
            # 1. Direct match
            if poster_type_key in agents_by_type:
                agents = agents_by_type[poster_type_key]
                idx = used_indices.get(poster_type_key, 0) % len(agents)
                matched_agent_id = agents[idx].agent_id
                matched_key = poster_type_key
                used_indices[poster_type_key] = idx + 1
            else:
                # 2. Alias-based match
                for alias_key, aliases in type_aliases.items():
                    normalized_aliases = [canonicalize_type(alias) for alias in aliases]
                    normalized_alias_key = canonicalize_type(alias_key)
                    if poster_type_key in normalized_aliases or normalized_alias_key == poster_type_key:
                        for alias in [normalized_alias_key, *normalized_aliases]:
                            if alias in agents_by_type:
                                agents = agents_by_type[alias]
                                idx = used_indices.get(alias, 0) % len(agents)
                                matched_agent_id = agents[idx].agent_id
                                matched_key = alias
                                used_indices[alias] = idx + 1
                                break
                    if matched_agent_id is not None:
                        break

                # 3. Token/substring similarity for near matches like "urban working household"
                if matched_agent_id is None and poster_type_key:
                    best_key = None
                    best_score = 0
                    poster_tokens = [token for token in re.findall(r"[a-z]+", poster_type) if len(token) >= 4]
                    for candidate_key, agents in agents_by_type.items():
                        score = 0
                        if poster_type_key and poster_type_key in candidate_key:
                            score += 3
                        for token in poster_tokens:
                            if token in candidate_key:
                                score += 1
                        if score > best_score and agents:
                            best_key = candidate_key
                            best_score = score
                    if best_key and best_score > 0:
                        agents = agents_by_type[best_key]
                        idx = used_indices.get(best_key, 0) % len(agents)
                        matched_agent_id = agents[idx].agent_id
                        matched_key = best_key
                        used_indices[best_key] = idx + 1
            
            # 4. If still unmatched, use the most influential agent
            if matched_agent_id is None:
                logger.warning(f"No matching agent was found for type '{poster_type}'. Using the most influential agent instead.")
                if agent_configs:
                    # Sort by influence and choose the most influential one
                    sorted_agents = sorted(agent_configs, key=lambda a: a.influence_weight, reverse=True)
                    matched_agent_id = sorted_agents[0].agent_id
                else:
                    matched_agent_id = 0
            
            updated_posts.append({
                "content": content,
                "poster_type": post.get("poster_type", "Unknown"),
                "poster_agent_id": matched_agent_id
            })
            
            logger.info(
                f"Initial post assignment: poster_type='{poster_type}' "
                f"(canonical='{poster_type_key}', matched='{matched_key or 'fallback'}') -> agent_id={matched_agent_id}"
            )
        
        event_config.initial_posts = updated_posts
        return event_config
    
    def _generate_agent_configs_batch(
        self,
        context: str,
        entities: List[EntityNode],
        start_idx: int,
        simulation_requirement: str
    ) -> List[AgentActivityConfig]:
        """Generate agent configurations in batches."""
        
        # Build entity information using the configured summary length
        entity_list = []
        summary_len = self.AGENT_SUMMARY_LENGTH
        for i, e in enumerate(entities):
            entity_list.append({
                "agent_id": start_idx + i,
                "entity_name": e.name,
                "entity_type": e.get_entity_type() or "Unknown",
                "summary": e.summary[:summary_len] if e.summary else ""
            })
        
        prompt = f"""Generate social media activity configurations for each entity based on the information below.

Simulation requirement: {simulation_requirement}

## Entity List
```json
{json.dumps(entity_list, ensure_ascii=False, indent=2)}
```

## Task
Generate an activity configuration for each entity. Note:
- **The schedule should follow a realistic local daily rhythm**: almost no activity from 00:00 to 05:00, with peak activity from 19:00 to 22:00
- **Official institutions** (`University` / `GovernmentAgency`): low activity level (0.1-0.3), active during working hours (09:00-17:00), slow response (60-240 minutes), high influence (2.5-3.0)
- **Media** (`MediaOutlet`): medium activity level (0.4-0.6), active all day (08:00-23:00), fast response (5-30 minutes), high influence (2.0-2.5)
- **Individuals** (`Student` / `Person` / `Alumni`): high activity level (0.6-0.9), mainly active in the evening (18:00-23:00), fast response (1-15 minutes), lower influence (0.8-1.2)
- **OPS public archetypes**:
  - `RuralHousehold`: moderate posting, high comment intensity, strong local influence chains
  - `UrbanWorkingFamily`: medium-high posting, fast response to price or wage shocks
  - `MiddleClassFamily`: medium posting, more cautious tone, moderate influence
  - `CorporateProfessional`: lower posting, more polished tone, higher professional influence
  - `MigrationWorker`: irregular posting windows, remittance-driven reaction timing, medium influence in family networks
  - `WomenHouseholdVoice`: moderate posting, strong community observation, higher reputation sensitivity
  - `ElderlyCitizen`: low posting, slow response, durable but narrower influence
- **Public figures / experts**: medium activity level (0.4-0.6), medium-to-high influence (1.5-2.0)

Return JSON only (no Markdown):
{{
    "agent_configs": [
        {{
            "agent_id": <must match the input>,
            "activity_level": <0.0-1.0>,
            "posts_per_hour": <posting frequency>,
            "comments_per_hour": <commenting frequency>,
            "active_hours": [<list of active hours aligned with the chosen daily schedule>],
            "response_delay_min": <minimum response delay in minutes>,
            "response_delay_max": <maximum response delay in minutes>,
            "sentiment_bias": <-1.0 to 1.0>,
            "stance": "<supportive/opposing/neutral/observer>",
            "influence_weight": <influence weight>
        }},
        ...
    ]
}}"""

        system_prompt = "You are a social media behavior analysis expert. Return pure JSON only. The configuration must follow a realistic local daily schedule."
        
        try:
            result = self._call_llm_with_retry(prompt, system_prompt)
            llm_configs = {cfg["agent_id"]: cfg for cfg in result.get("agent_configs", [])}
        except Exception as e:
            logger.warning(f"LLM generation for the agent configuration batch failed: {e}. Falling back to rule-based generation.")
            llm_configs = {}
        
        # Build `AgentActivityConfig` objects
        configs = []
        for i, entity in enumerate(entities):
            agent_id = start_idx + i
            cfg = llm_configs.get(agent_id, {})
            
            # If the LLM did not generate a config, fall back to the rule-based version
            if not cfg:
                cfg = self._generate_agent_config_by_rule(entity)
            
            config = AgentActivityConfig(
                agent_id=agent_id,
                entity_uuid=entity.uuid,
                entity_name=entity.name,
                entity_type=entity.get_entity_type() or "Unknown",
                activity_level=cfg.get("activity_level", 0.5),
                posts_per_hour=cfg.get("posts_per_hour", 0.5),
                comments_per_hour=cfg.get("comments_per_hour", 1.0),
                active_hours=cfg.get("active_hours", list(range(9, 23))),
                response_delay_min=cfg.get("response_delay_min", 5),
                response_delay_max=cfg.get("response_delay_max", 60),
                sentiment_bias=cfg.get("sentiment_bias", 0.0),
                stance=cfg.get("stance", "neutral"),
                influence_weight=cfg.get("influence_weight", 1.0)
            )
            configs.append(config)
        
        return configs
    
    def _generate_agent_config_by_rule(self, entity: EntityNode) -> Dict[str, Any]:
        """Generate a single agent configuration using rules based on a realistic local daily schedule."""
        entity_type = (entity.get_entity_type() or "Unknown").lower()
        
        if entity_type in ["university", "governmentagency", "ngo"]:
            # Official institutions: active during working hours, low frequency, high influence
            return {
                "activity_level": 0.2,
                "posts_per_hour": 0.1,
                "comments_per_hour": 0.05,
                "active_hours": list(range(9, 18)),  # 9:00-17:59
                "response_delay_min": 60,
                "response_delay_max": 240,
                "sentiment_bias": 0.0,
                "stance": "neutral",
                "influence_weight": 3.0
            }
        elif entity_type in ["mediaoutlet"]:
            # Media: active all day, medium frequency, high influence
            return {
                "activity_level": 0.5,
                "posts_per_hour": 0.8,
                "comments_per_hour": 0.3,
                "active_hours": list(range(7, 24)),  # 7:00-23:59
                "response_delay_min": 5,
                "response_delay_max": 30,
                "sentiment_bias": 0.0,
                "stance": "observer",
                "influence_weight": 2.5
            }
        elif entity_type in ["professor", "expert", "official"]:
            # Experts/professors: active during work hours and in the evening, medium frequency
            return {
                "activity_level": 0.4,
                "posts_per_hour": 0.3,
                "comments_per_hour": 0.5,
                "active_hours": list(range(8, 22)),  # 8:00-21:59
                "response_delay_min": 15,
                "response_delay_max": 90,
                "sentiment_bias": 0.0,
                "stance": "neutral",
                "influence_weight": 2.0
            }
        elif entity_type in ["student"]:
            # Students: mainly active in the evening, high frequency
            return {
                "activity_level": 0.8,
                "posts_per_hour": 0.6,
                "comments_per_hour": 1.5,
                "active_hours": [8, 9, 10, 11, 12, 13, 18, 19, 20, 21, 22, 23],  # Morning + evening
                "response_delay_min": 1,
                "response_delay_max": 15,
                "sentiment_bias": 0.0,
                "stance": "neutral",
                "influence_weight": 0.8
            }
        elif entity_type in ["alumni"]:
            # Alumni: mainly active in the evening
            return {
                "activity_level": 0.6,
                "posts_per_hour": 0.4,
                "comments_per_hour": 0.8,
                "active_hours": [12, 13, 19, 20, 21, 22, 23],  # Lunch break + evening
                "response_delay_min": 5,
                "response_delay_max": 30,
                "sentiment_bias": 0.0,
                "stance": "neutral",
                "influence_weight": 1.0
            }
        else:
            # Ordinary people: evening peak
            return {
                "activity_level": 0.7,
                "posts_per_hour": 0.5,
                "comments_per_hour": 1.2,
                "active_hours": [9, 10, 11, 12, 13, 18, 19, 20, 21, 22, 23],  # Daytime + evening
                "response_delay_min": 2,
                "response_delay_max": 20,
                "sentiment_bias": 0.0,
                "stance": "neutral",
                "influence_weight": 1.0
            }
    

