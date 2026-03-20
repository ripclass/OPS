"""
OASIS agent profile generator.
Converts entities in the Zep graph into the agent profile format required by the OASIS simulation platform.

Enhancements:
1. Use Zep retrieval to enrich node information a second time
2. Improve prompts to generate much more detailed personas
3. Distinguish individual entities from abstract group entities
"""

import json
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI
from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from .zep_entity_reader import EntityNode, ZepEntityReader

logger = get_logger('mirofish.oasis_profile')


@dataclass
class OasisAgentProfile:
    """OASIS agent profile data structure."""
    # Common fields
    user_id: int
    user_name: str
    name: str
    bio: str
    persona: str
    
    # Optional fields - Reddit style
    karma: int = 1000
    
    # Optional fields - Twitter style
    friend_count: int = 100
    follower_count: int = 150
    statuses_count: int = 500
    
    # Additional persona information
    age: Optional[int] = None
    gender: Optional[str] = None
    mbti: Optional[str] = None
    country: Optional[str] = None
    profession: Optional[str] = None
    interested_topics: List[str] = field(default_factory=list)
    trust_government: Optional[int] = None
    shame_sensitivity: Optional[int] = None
    primary_fear: Optional[str] = None
    influence_radius: Optional[int] = None
    fb_intensity: Optional[int] = None
    dialect: Optional[str] = None
    income_stability: Optional[str] = None
    rumour_amplifier: Optional[bool] = None
    
    # Source entity information
    source_entity_uuid: Optional[str] = None
    source_entity_type: Optional[str] = None
    
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def ops_fields(self) -> Dict[str, Any]:
        """OPS-specific persona fields."""
        return {
            "trust_government": self.trust_government,
            "shame_sensitivity": self.shame_sensitivity,
            "primary_fear": self.primary_fear,
            "influence_radius": self.influence_radius,
            "fb_intensity": self.fb_intensity,
            "dialect": self.dialect,
            "income_stability": self.income_stability,
            "rumour_amplifier": self.rumour_amplifier,
        }

    def build_user_char(self) -> str:
        """Compose the text prompt OASIS injects for Twitter agents."""
        parts = [self.bio]
        if self.persona and self.persona != self.bio:
            parts.append(self.persona)

        ops_pairs = []
        for key, value in self.ops_fields().items():
            if value is None:
                continue
            if isinstance(value, bool):
                rendered = str(value).lower()
            else:
                rendered = str(value)
            ops_pairs.append(f"{key}={rendered}")

        if ops_pairs:
            parts.append("OPS persona: " + ", ".join(ops_pairs))

        return " ".join(part for part in parts if part).replace('\n', ' ').replace('\r', ' ')

    def _apply_optional_fields(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Attach optional persona fields, preserving falsy but valid values such as 0/False."""
        if self.age is not None:
            profile["age"] = self.age
        if self.gender:
            profile["gender"] = self.gender
        if self.mbti:
            profile["mbti"] = self.mbti
        if self.country:
            profile["country"] = self.country
        if self.profession:
            profile["profession"] = self.profession
        if self.interested_topics:
            profile["interested_topics"] = self.interested_topics

        for key, value in self.ops_fields().items():
            if value is not None:
                profile[key] = value

        return profile
    
    def to_reddit_format(self) -> Dict[str, Any]:
        """Convert to Reddit platform format."""
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,  # The OASIS library requires `username` without an underscore
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "created_at": self.created_at,
        }
        return self._apply_optional_fields(profile)
    
    def to_twitter_format(self) -> Dict[str, Any]:
        """Convert to Twitter platform format."""
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,  # The OASIS library requires `username` without an underscore
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
        }
        return self._apply_optional_fields(profile)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a full dictionary representation."""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "age": self.age,
            "gender": self.gender,
            "mbti": self.mbti,
            "country": self.country,
            "profession": self.profession,
            "interested_topics": self.interested_topics,
            **self.ops_fields(),
            "source_entity_uuid": self.source_entity_uuid,
            "source_entity_type": self.source_entity_type,
            "created_at": self.created_at,
        }


class OasisProfileGenerator:
    """
    OASIS profile generator.

    Converts entities in the Zep graph into the agent profiles required by OASIS simulations.

    Enhanced features:
    1. Use Zep graph retrieval to get richer context
    2. Generate highly detailed personas, including basic information, professional history, personality traits, and social media behavior
    3. Distinguish between individual entities and abstract group entities
    """
    
    # List of MBTI types
    MBTI_TYPES = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP"
    ]
    
    # Common countries
    COUNTRIES = [
        "China", "US", "UK", "Japan", "Germany", "France", 
        "Canada", "Australia", "Brazil", "India", "South Korea"
    ]
    
    # Individual-type entities that require concrete personas
    INDIVIDUAL_ENTITY_TYPES = [
        "student", "alumni", "professor", "person", "publicfigure", 
        "expert", "faculty", "official", "journalist", "activist"
    ]
    
    # Group/institution entity types that require representative account personas
    GROUP_ENTITY_TYPES = [
        "university", "governmentagency", "organization", "ngo", 
        "mediaoutlet", "company", "institution", "group", "community"
    ]
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        zep_api_key: Optional[str] = None,
        graph_id: Optional[str] = None
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
        
        # Zep client used to retrieve richer context
        self.zep_api_key = zep_api_key or Config.ZEP_API_KEY
        self.zep_client = None
        self.graph_id = graph_id
        
        if self.zep_api_key:
            try:
                self.zep_client = Zep(api_key=self.zep_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize the Zep client: {e}")
    
    def generate_profile_from_entity(
        self, 
        entity: EntityNode, 
        user_id: int,
        use_llm: bool = True
    ) -> OasisAgentProfile:
        """
        Generate an OASIS agent profile from a Zep entity.
        
        Args:
            entity: Zep entity node
            user_id: User ID used by OASIS
            use_llm: Whether to use the LLM to generate a detailed persona
            
        Returns:
            OasisAgentProfile
        """
        entity_type = entity.get_entity_type() or "Entity"
        
        # Basic information
        name = entity.name
        user_name = self._generate_username(name)
        
        # Build the context information
        context = self._build_entity_context(entity)
        
        if use_llm:
            # Use the LLM to generate a detailed persona
            profile_data = self._generate_profile_with_llm(
                entity_name=name,
                entity_type=entity_type,
                entity_summary=entity.summary,
                entity_attributes=entity.attributes,
                context=context
            )
        else:
            # Use rules to generate a basic persona
            profile_data = self._generate_profile_rule_based(
                entity_name=name,
                entity_type=entity_type,
                entity_summary=entity.summary,
                entity_attributes=entity.attributes
            )
        
        return OasisAgentProfile(
            user_id=user_id,
            user_name=user_name,
            name=name,
            bio=profile_data.get("bio", f"{entity_type}: {name}"),
            persona=profile_data.get("persona", entity.summary or f"A {entity_type} named {name}."),
            karma=profile_data.get("karma", random.randint(500, 5000)),
            friend_count=profile_data.get("friend_count", random.randint(50, 500)),
            follower_count=profile_data.get("follower_count", random.randint(100, 1000)),
            statuses_count=profile_data.get("statuses_count", random.randint(100, 2000)),
            age=profile_data.get("age"),
            gender=profile_data.get("gender"),
            mbti=profile_data.get("mbti"),
            country=profile_data.get("country"),
            profession=profile_data.get("profession"),
            interested_topics=profile_data.get("interested_topics", []),
            trust_government=profile_data.get("trust_government"),
            shame_sensitivity=profile_data.get("shame_sensitivity"),
            primary_fear=profile_data.get("primary_fear"),
            influence_radius=profile_data.get("influence_radius"),
            fb_intensity=profile_data.get("fb_intensity"),
            dialect=profile_data.get("dialect"),
            income_stability=profile_data.get("income_stability"),
            rumour_amplifier=profile_data.get("rumour_amplifier"),
            source_entity_uuid=entity.uuid,
            source_entity_type=entity_type,
        )
    
    def _generate_username(self, name: str) -> str:
        """Generate a username."""
        # Remove special characters and convert to lowercase
        username = name.lower().replace(" ", "_")
        username = ''.join(c for c in username if c.isalnum() or c == '_')
        
        # Add a random suffix to avoid duplicates
        suffix = random.randint(100, 999)
        return f"{username}_{suffix}"
    
    def _search_zep_for_entity(self, entity: EntityNode) -> Dict[str, Any]:
        """
        Use mixed Zep graph search to retrieve richer information related to the entity.

        Zep does not provide a built-in mixed-search endpoint, so edges and nodes are searched separately and then merged.
        Parallel requests are used to improve performance.
        
        Args:
            entity: Entity node object
            
        Returns:
            A dictionary containing `facts`, `node_summaries`, and `context`
        """
        import concurrent.futures
        
        if not self.zep_client:
            return {"facts": [], "node_summaries": [], "context": ""}
        
        entity_name = entity.name
        
        results = {
            "facts": [],
            "node_summaries": [],
            "context": ""
        }
        
        # A `graph_id` is required before searching
        if not self.graph_id:
            logger.debug("Skipping Zep retrieval because `graph_id` is not set")
            return results
        
        comprehensive_query = f"All information, activities, events, relationships, and background about {entity_name}"
        
        def search_edges():
            """Search edges, facts, and relationships with retry logic."""
            max_retries = 3
            last_exception = None
            delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    return self.zep_client.graph.search(
                        query=comprehensive_query,
                        graph_id=self.graph_id,
                        limit=30,
                        scope="edges",
                        reranker="rrf"
                    )
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.debug(f"Zep edge search attempt {attempt + 1} failed: {str(e)[:80]}, retrying...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.debug(f"Zep edge search still failed after {max_retries} attempts: {e}")
            return None
        
        def search_nodes():
            """Search nodes and entity summaries with retry logic."""
            max_retries = 3
            last_exception = None
            delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    return self.zep_client.graph.search(
                        query=comprehensive_query,
                        graph_id=self.graph_id,
                        limit=20,
                        scope="nodes",
                        reranker="rrf"
                    )
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.debug(f"Zep node search attempt {attempt + 1} failed: {str(e)[:80]}, retrying...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.debug(f"Zep node search still failed after {max_retries} attempts: {e}")
            return None
        
        try:
            # Run edge and node searches in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                edge_future = executor.submit(search_edges)
                node_future = executor.submit(search_nodes)
                
                # Collect the results
                edge_result = edge_future.result(timeout=30)
                node_result = node_future.result(timeout=30)
            
            # Process edge-search results
            all_facts = set()
            if edge_result and hasattr(edge_result, 'edges') and edge_result.edges:
                for edge in edge_result.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        all_facts.add(edge.fact)
            results["facts"] = list(all_facts)
            
            # Process node-search results
            all_summaries = set()
            if node_result and hasattr(node_result, 'nodes') and node_result.nodes:
                for node in node_result.nodes:
                    if hasattr(node, 'summary') and node.summary:
                        all_summaries.add(node.summary)
                    if hasattr(node, 'name') and node.name and node.name != entity_name:
                        all_summaries.add(f"Related entity: {node.name}")
            results["node_summaries"] = list(all_summaries)
            
            # Build the combined context
            context_parts = []
            if results["facts"]:
                context_parts.append("Facts:\n" + "\n".join(f"- {f}" for f in results["facts"][:20]))
            if results["node_summaries"]:
                context_parts.append("Related entities:\n" + "\n".join(f"- {s}" for s in results["node_summaries"][:10]))
            results["context"] = "\n\n".join(context_parts)
            
            logger.info(f"Completed Zep mixed retrieval for {entity_name}: {len(results['facts'])} facts and {len(results['node_summaries'])} related nodes")
            
        except concurrent.futures.TimeoutError:
            logger.warning(f"Zep retrieval timed out for {entity_name}")
        except Exception as e:
            logger.warning(f"Zep retrieval failed for {entity_name}: {e}")
        
        return results
    
    def _build_entity_context(self, entity: EntityNode) -> str:
        """
        Build the entity's full context information.

        Includes:
        1. The entity's own edge information, such as facts
        2. Detailed information about related nodes
        3. Rich information retrieved through Zep mixed search
        """
        context_parts = []
        
        # 1. Add entity attribute information
        if entity.attributes:
            attrs = []
            for key, value in entity.attributes.items():
                if value and str(value).strip():
                    attrs.append(f"- {key}: {value}")
            if attrs:
                context_parts.append("### Entity Attributes\n" + "\n".join(attrs))
        
        # 2. Add related edge information, such as facts and relationships
        existing_facts = set()
        if entity.related_edges:
            relationships = []
            for edge in entity.related_edges:  # No limit
                fact = edge.get("fact", "")
                edge_name = edge.get("edge_name", "")
                direction = edge.get("direction", "")
                
                if fact:
                    relationships.append(f"- {fact}")
                    existing_facts.add(fact)
                elif edge_name:
                    if direction == "outgoing":
                        relationships.append(f"- {entity.name} --[{edge_name}]--> (related entity)")
                    else:
                        relationships.append(f"- (related entity) --[{edge_name}]--> {entity.name}")
            
            if relationships:
                context_parts.append("### Related Facts and Relationships\n" + "\n".join(relationships))
        
        # 3. Add detailed information for related nodes
        if entity.related_nodes:
            related_info = []
            for node in entity.related_nodes:  # No limit
                node_name = node.get("name", "")
                node_labels = node.get("labels", [])
                node_summary = node.get("summary", "")
                
                # Filter out default labels
                custom_labels = [l for l in node_labels if l not in ["Entity", "Node"]]
                label_str = f" ({', '.join(custom_labels)})" if custom_labels else ""
                
                if node_summary:
                    related_info.append(f"- **{node_name}**{label_str}: {node_summary}")
                else:
                    related_info.append(f"- **{node_name}**{label_str}")
            
            if related_info:
                context_parts.append("### Related Entity Information\n" + "\n".join(related_info))
        
        # 4. Use Zep mixed retrieval to get richer information
        zep_results = self._search_zep_for_entity(entity)
        
        if zep_results.get("facts"):
            # De-duplicate by excluding facts already present
            new_facts = [f for f in zep_results["facts"] if f not in existing_facts]
            if new_facts:
                context_parts.append("### Facts Retrieved from Zep\n" + "\n".join(f"- {f}" for f in new_facts[:15]))
        
        if zep_results.get("node_summaries"):
            context_parts.append("### Related Nodes Retrieved from Zep\n" + "\n".join(f"- {s}" for s in zep_results["node_summaries"][:10]))
        
        return "\n\n".join(context_parts)
    
    def _is_individual_entity(self, entity_type: str) -> bool:
        """Check whether this is an individual-type entity."""
        return entity_type.lower() in self.INDIVIDUAL_ENTITY_TYPES
    
    def _is_group_entity(self, entity_type: str) -> bool:
        """Check whether this is a group or institution entity."""
        return entity_type.lower() in self.GROUP_ENTITY_TYPES
    
    def _generate_profile_with_llm(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> Dict[str, Any]:
        """
        Use the LLM to generate a highly detailed persona.

        The output differs by entity type:
        - Individual entities: generate a concrete character profile
        - Group or institution entities: generate a representative account profile
        """
        
        is_individual = self._is_individual_entity(entity_type)
        
        if is_individual:
            prompt = self._build_individual_persona_prompt(
                entity_name, entity_type, entity_summary, entity_attributes, context
            )
        else:
            prompt = self._build_group_persona_prompt(
                entity_name, entity_type, entity_summary, entity_attributes, context
            )

        # Retry until success or the maximum retry count is reached
        max_attempts = 3
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(is_individual)},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7 - (attempt * 0.1)  # Lower the temperature on each retry
                    # Do not set `max_tokens`; allow the LLM to respond freely
                )
                
                content = response.choices[0].message.content
                
                # Check whether the output was truncated (`finish_reason` is not `stop`)
                finish_reason = response.choices[0].finish_reason
                if finish_reason == 'length':
                    logger.warning(f"LLM output was truncated (attempt {attempt+1}); attempting repair...")
                    content = self._fix_truncated_json(content)
                
                # Try to parse the JSON
                try:
                    result = json.loads(content)
                    
                    # Validate required fields
                    if "bio" not in result or not result["bio"]:
                        result["bio"] = entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}"
                    if "persona" not in result or not result["persona"]:
                        result["persona"] = entity_summary or f"{entity_name} is a {entity_type}."
                    
                    return result
                    
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON parsing failed (attempt {attempt+1}): {str(je)[:80]}")
                    
                    # Attempt to repair the JSON
                    result = self._try_fix_json(content, entity_name, entity_type, entity_summary)
                    if result.get("_fixed"):
                        del result["_fixed"]
                        return result
                    
                    last_error = je
                    
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt+1}): {str(e)[:80]}")
                last_error = e
                import time
                time.sleep(1 * (attempt + 1))  # Exponential backoff
        
        logger.warning(f"LLM persona generation failed after {max_attempts} attempts: {last_error}. Falling back to rule-based generation.")
        return self._generate_profile_rule_based(
            entity_name, entity_type, entity_summary, entity_attributes
        )
    
    def _fix_truncated_json(self, content: str) -> str:
        """Repair truncated JSON when the output is cut off by a token limit."""
        import re
        
        # If the JSON was truncated, try to close it
        content = content.strip()
        
        # Count unclosed braces and brackets
        open_braces = content.count('{') - content.count('}')
        open_brackets = content.count('[') - content.count(']')
        
        # Check for an unclosed string
        # Simple heuristic: if the last character is not a quote, comma, or closing brace/bracket, the string may be truncated
        if content and content[-1] not in '",}]':
            # Try to close the string
            content += '"'
        
        # Close brackets and braces
        content += ']' * open_brackets
        content += '}' * open_braces
        
        return content
    
    def _try_fix_json(self, content: str, entity_name: str, entity_type: str, entity_summary: str = "") -> Dict[str, Any]:
        """Attempt to repair malformed JSON."""
        import re
        
        # 1. First try to repair truncation
        content = self._fix_truncated_json(content)
        
        # 2. Try to extract the JSON portion
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            
            # 3. Fix newline issues inside string values
            def fix_string_newlines(match):
                s = match.group(0)
                # Replace literal newlines inside strings with spaces
                s = s.replace('\n', ' ').replace('\r', ' ')
                # Collapse extra whitespace
                s = re.sub(r'\s+', ' ', s)
                return s
            
            # Match JSON string values
            json_str = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', fix_string_newlines, json_str)
            
            # 4. Try to parse
            try:
                result = json.loads(json_str)
                result["_fixed"] = True
                return result
            except json.JSONDecodeError as e:
                # 5. If that still fails, attempt a more aggressive repair
                try:
                    # Remove all control characters
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
                    # Collapse all consecutive whitespace
                    json_str = re.sub(r'\s+', ' ', json_str)
                    result = json.loads(json_str)
                    result["_fixed"] = True
                    return result
                except:
                    pass
        
        # 6. Try to extract partial information from the content
        bio_match = re.search(r'"bio"\s*:\s*"([^"]*)"', content)
        persona_match = re.search(r'"persona"\s*:\s*"([^"]*)', content)  # May be truncated
        
        bio = bio_match.group(1) if bio_match else (entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}")
        persona = persona_match.group(1) if persona_match else (entity_summary or f"{entity_name} is a {entity_type}.")
        
        # If meaningful content was extracted, mark the result as repaired
        if bio_match or persona_match:
            logger.info("Extracted partial information from malformed JSON")
            return {
                "bio": bio,
                "persona": persona,
                "_fixed": True
            }
        
        # 7. Full failure: return a basic structure
        logger.warning("JSON repair failed; returning a basic structure")
        return {
            "bio": entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}",
            "persona": entity_summary or f"{entity_name} is a {entity_type}."
        }
    
    def _get_system_prompt(self, is_individual: bool) -> str:
        """Get the system prompt."""
        base_prompt = "You are a social media persona generation expert. Generate detailed, realistic personas for public-opinion simulation and stay as faithful as possible to the existing real-world situation. You must return valid JSON, and string values must not contain unescaped newlines. Use English."
        return base_prompt
    
    def _build_individual_persona_prompt(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> str:
        """Build the detailed persona prompt for an individual entity."""
        
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "None"
        context_str = context[:3000] if context else "No additional context"
        
        return f"""Generate a detailed social-media user persona for the entity below, staying as faithful as possible to the existing real-world situation.

Entity name: {entity_name}
Entity type: {entity_type}
Entity summary: {entity_summary}
Entity attributes: {attrs_str}

Context:
{context_str}

Generate JSON with the following fields:

1. bio: a 200-word social media bio
2. persona: a detailed persona description in plain text, about 2000 words, including:
   - basic information such as age, profession, education, and location
   - personal background such as major experiences, relationship to the event, and social ties
   - personality traits such as MBTI, core disposition, and emotional expression style
   - social media behavior such as posting frequency, content preferences, interaction style, and language habits
   - viewpoints and stance, including attitudes toward the topic and what might anger or move this person
   - unique traits such as catchphrases, unusual experiences, and hobbies
   - personal memory, which is an important part of the persona and should describe how this individual relates to the event and what actions and reactions they have already shown
3. age: numeric age (must be an integer)
4. gender: must be in English, either "male" or "female"
5. mbti: MBTI type such as INTJ or ENFP
6. country: country name in English, such as "China"
7. profession: profession
8. interested_topics: array of topics of interest
9. trust_government: trust in government, integer from 0 to 10
10. shame_sensitivity: shame sensitivity, integer from 0 to 10
11. primary_fear: the person's core immediate fear, string
12. influence_radius: approximate number of people they can influence, integer
13. fb_intensity: Facebook or social media usage intensity, integer from 0 to 10
14. dialect: usual dialect or colloquial style, string
15. income_stability: description of income stability, string
16. rumour_amplifier: whether the person tends to amplify or relay rumors, boolean `true` or `false`

Important:
- All field values must be strings, numbers, booleans, or arrays as appropriate; do not use unescaped newlines
- `persona` must be a single coherent block of text
- Use English, except that `gender` must still be "male" or "female"
- Keep the content consistent with the entity information
- `age` must be a valid integer, and `gender` must be "male" or "female"
- `trust_government`, `shame_sensitivity`, and `fb_intensity` must be integers between 0 and 10
- `influence_radius` must be an integer, and `rumour_amplifier` must be `true` or `false`
- The `persona` should naturally reflect how these OPS variables shape the entity's speech and information-sharing behavior
"""

    def _build_group_persona_prompt(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> str:
        """Build the detailed persona prompt for a group or institution entity."""
        
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "None"
        context_str = context[:3000] if context else "No additional context"
        
        return f"""Generate a detailed social-media account profile for the organization or group below, staying as faithful as possible to the existing real-world situation.

Entity name: {entity_name}
Entity type: {entity_type}
Entity summary: {entity_summary}
Entity attributes: {attrs_str}

Context:
{context_str}

Generate JSON with the following fields:

1. bio: professional public account bio, about 200 words
2. persona: detailed account profile in plain text, about 2000 words, including:
   - basic institutional information such as formal name, institutional nature, founding background, and primary functions
   - account positioning such as account type, target audience, and core role
   - speaking style such as language traits, common expressions, and taboo topics
   - content patterns such as content type, posting frequency, and active hours
   - stance and posture, such as the institution's official position on key topics and how it handles controversy
   - special notes such as the profile of the represented group and operating habits
   - institutional memory, which is an important part of the persona and should describe how the institution relates to the event and what actions and reactions it has already shown
3. age: fixed at 30 as the account's virtual age
4. gender: fixed to "other" because the account is non-personal
5. mbti: MBTI type used to describe account style, for example ISTJ for a rigorous and conservative tone
6. country: country name in English, such as "China"
7. profession: description of the institution's function
8. interested_topics: array of focus areas
9. trust_government: trust in government, integer from 0 to 10
10. shame_sensitivity: shame sensitivity, integer from 0 to 10
11. primary_fear: the account's core immediate concern, string
12. influence_radius: approximate number of people the account can influence, integer
13. fb_intensity: Facebook or social media usage intensity, integer from 0 to 10
14. dialect: usual dialect or colloquial style, string
15. income_stability: description of income stability, string
16. rumour_amplifier: whether the account tends to amplify or relay rumors, boolean `true` or `false`

Important:
- All field values must be strings, numbers, booleans, or arrays as appropriate; `null` is not allowed
- `persona` must be a single coherent block of text with no unescaped newlines
- Use English, except that `gender` must be the English string `"other"`
- `age` must be the integer `30`, and `gender` must be `"other"`
- The institution's voice must match its identity and role"""
    
    def _generate_profile_rule_based(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a basic persona using rules."""
        
        # Generate different personas based on entity type
        entity_type_lower = entity_type.lower()
        
        if entity_type_lower in ["student", "alumni"]:
            return {
                "bio": f"{entity_type} with interests in academics and social issues.",
                "persona": f"{entity_name} is a {entity_type.lower()} who is actively engaged in academic and social discussions. They enjoy sharing perspectives and connecting with peers.",
                "age": random.randint(18, 30),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES),
                "country": random.choice(self.COUNTRIES),
                "profession": "Student",
                "interested_topics": ["Education", "Social Issues", "Technology"],
                "trust_government": random.randint(3, 7),
                "shame_sensitivity": random.randint(4, 8),
                "primary_fear": "education costs",
                "influence_radius": random.randint(10, 40),
                "fb_intensity": random.randint(5, 9),
                "dialect": "standard",
                "income_stability": "unstable",
                "rumour_amplifier": random.choice([True, False]),
            }
        
        elif entity_type_lower in ["publicfigure", "expert", "faculty"]:
            return {
                "bio": f"Expert and thought leader in their field.",
                "persona": f"{entity_name} is a recognized {entity_type.lower()} who shares insights and opinions on important matters. They are known for their expertise and influence in public discourse.",
                "age": random.randint(35, 60),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(["ENTJ", "INTJ", "ENTP", "INTP"]),
                "country": random.choice(self.COUNTRIES),
                "profession": entity_attributes.get("occupation", "Expert"),
                "interested_topics": ["Politics", "Economics", "Culture & Society"],
                "trust_government": random.randint(4, 8),
                "shame_sensitivity": random.randint(2, 6),
                "primary_fear": "loss of credibility",
                "influence_radius": random.randint(100, 1000),
                "fb_intensity": random.randint(3, 7),
                "dialect": "standard",
                "income_stability": "stable",
                "rumour_amplifier": False,
            }
        
        elif entity_type_lower in ["mediaoutlet", "socialmediaplatform"]:
            return {
                "bio": f"Official account for {entity_name}. News and updates.",
                "persona": f"{entity_name} is a media entity that reports news and facilitates public discourse. The account shares timely updates and engages with the audience on current events.",
                "age": 30,  # Virtual age for institution accounts
                "gender": "other",  # Institutions use `other`
                "mbti": "ISTJ",  # Institutional style: rigorous and conservative
                "country": "China",
                "profession": "Media",
                "interested_topics": ["General News", "Current Events", "Public Affairs"],
                "trust_government": 5,
                "shame_sensitivity": 2,
                "primary_fear": "audience distrust",
                "influence_radius": random.randint(500, 5000),
                "fb_intensity": 8,
                "dialect": "standard",
                "income_stability": "institutional",
                "rumour_amplifier": False,
            }
        
        elif entity_type_lower in ["university", "governmentagency", "ngo", "organization"]:
            return {
                "bio": f"Official account of {entity_name}.",
                "persona": f"{entity_name} is an institutional entity that communicates official positions, announcements, and engages with stakeholders on relevant matters.",
                "age": 30,  # Virtual age for institution accounts
                "gender": "other",  # Institutions use `other`
                "mbti": "ISTJ",  # Institutional style: rigorous and conservative
                "country": "China",
                "profession": entity_type,
                "interested_topics": ["Public Policy", "Community", "Official Announcements"],
                "trust_government": 7,
                "shame_sensitivity": 3,
                "primary_fear": "public backlash",
                "influence_radius": random.randint(200, 3000),
                "fb_intensity": 4,
                "dialect": "standard",
                "income_stability": "institutional",
                "rumour_amplifier": False,
            }
        
        else:
            # Default persona
            return {
                "bio": entity_summary[:150] if entity_summary else f"{entity_type}: {entity_name}",
                "persona": entity_summary or f"{entity_name} is a {entity_type.lower()} participating in social discussions.",
                "age": random.randint(25, 50),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES),
                "country": random.choice(self.COUNTRIES),
                "profession": entity_type,
                "interested_topics": ["General", "Social Issues"],
                "trust_government": random.randint(2, 7),
                "shame_sensitivity": random.randint(3, 8),
                "primary_fear": "household costs",
                "influence_radius": random.randint(10, 80),
                "fb_intensity": random.randint(3, 8),
                "dialect": "standard",
                "income_stability": "variable",
                "rumour_amplifier": random.choice([True, False]),
            }
    
    def set_graph_id(self, graph_id: str):
        """Set the graph ID used for Zep retrieval."""
        self.graph_id = graph_id
    
    def generate_profiles_from_entities(
        self,
        entities: List[EntityNode],
        use_llm: bool = True,
        progress_callback: Optional[callable] = None,
        graph_id: Optional[str] = None,
        parallel_count: int = 5,
        realtime_output_path: Optional[str] = None,
        output_platform: str = "reddit"
    ) -> List[OasisAgentProfile]:
        """
        Generate agent profiles from entities in batch, with parallel execution support.
        
        Args:
            entities: List of entities
            use_llm: Whether to use the LLM to generate detailed personas
            progress_callback: Progress callback function `(current, total, message)`
            graph_id: Graph ID used for Zep retrieval to obtain richer context
            parallel_count: Number of parallel generations, defaults to 5
            realtime_output_path: File path for real-time writes; if provided, write after each profile is generated
            output_platform: Output platform format, `"reddit"` or `"twitter"`
            
        Returns:
            List of agent profiles
        """
        import concurrent.futures
        from threading import Lock
        
        # Set the `graph_id` for Zep retrieval
        if graph_id:
            self.graph_id = graph_id
        
        total = len(entities)
        profiles = [None] * total  # Preallocate the list to preserve order
        completed_count = [0]  # Use a list so it can be mutated inside closures
        lock = Lock()
        
        # Helper for writing profiles to disk in real time
        def save_profiles_realtime():
            """Save already-generated profiles to disk in real time."""
            if not realtime_output_path:
                return
            
            with lock:
                # Keep only profiles that have already been generated
                existing_profiles = [p for p in profiles if p is not None]
                if not existing_profiles:
                    return
                
                try:
                    if output_platform == "reddit":
                        # Reddit JSON format
                        profiles_data = [p.to_reddit_format() for p in existing_profiles]
                        with open(realtime_output_path, 'w', encoding='utf-8') as f:
                            json.dump(profiles_data, f, ensure_ascii=False, indent=2)
                    else:
                        # Twitter CSV format
                        import csv
                        profiles_data = [p.to_twitter_format() for p in existing_profiles]
                        if profiles_data:
                            fieldnames = list(profiles_data[0].keys())
                            with open(realtime_output_path, 'w', encoding='utf-8', newline='') as f:
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(profiles_data)
                except Exception as e:
                    logger.warning(f"Failed to save profiles in real time: {e}")
        
        def generate_single_profile(idx: int, entity: EntityNode) -> tuple:
            """Worker function for generating a single profile."""
            entity_type = entity.get_entity_type() or "Entity"
            
            try:
                profile = self.generate_profile_from_entity(
                    entity=entity,
                    user_id=idx,
                    use_llm=use_llm
                )
                
                # Print the generated persona to the console in real time
                self._print_generated_profile(entity.name, entity_type, profile)
                
                return idx, profile, None
                
            except Exception as e:
                logger.error(f"Failed to generate a persona for entity {entity.name}: {str(e)}")
                # Create a basic fallback profile
                fallback_profile = OasisAgentProfile(
                    user_id=idx,
                    user_name=self._generate_username(entity.name),
                    name=entity.name,
                    bio=f"{entity_type}: {entity.name}",
                    persona=entity.summary or f"A participant in social discussions.",
                    source_entity_uuid=entity.uuid,
                    source_entity_type=entity_type,
                )
                return idx, fallback_profile, str(e)
        
        logger.info(f"Starting parallel generation of {total} agent personas (parallelism: {parallel_count})...")
        print(f"\n{'='*60}")
        print(f"Starting agent persona generation: {total} entities, parallelism {parallel_count}")
        print(f"{'='*60}\n")
        
        # Execute in parallel with a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
            # Submit all tasks
            future_to_entity = {
                executor.submit(generate_single_profile, idx, entity): (idx, entity)
                for idx, entity in enumerate(entities)
            }
            
            # Collect the results
            for future in concurrent.futures.as_completed(future_to_entity):
                idx, entity = future_to_entity[future]
                entity_type = entity.get_entity_type() or "Entity"
                
                try:
                    result_idx, profile, error = future.result()
                    profiles[result_idx] = profile
                    
                    with lock:
                        completed_count[0] += 1
                        current = completed_count[0]
                    
                    # Save to disk in real time
                    save_profiles_realtime()
                    
                    if progress_callback:
                        progress_callback(
                            current, 
                            total, 
                            f"Completed {current}/{total}: {entity.name} ({entity_type})"
                        )
                    
                    if error:
                        logger.warning(f"[{current}/{total}] {entity.name} used a fallback persona: {error}")
                    else:
                        logger.info(f"[{current}/{total}] Successfully generated persona: {entity.name} ({entity_type})")
                        
                except Exception as e:
                    logger.error(f"Unexpected error while processing entity {entity.name}: {str(e)}")
                    with lock:
                        completed_count[0] += 1
                    profiles[idx] = OasisAgentProfile(
                        user_id=idx,
                        user_name=self._generate_username(entity.name),
                        name=entity.name,
                        bio=f"{entity_type}: {entity.name}",
                        persona=entity.summary or "A participant in social discussions.",
                        source_entity_uuid=entity.uuid,
                        source_entity_type=entity_type,
                    )
                    # Save in real time even for fallback personas
                    save_profiles_realtime()
        
        print(f"\n{'='*60}")
        print(f"Persona generation complete. Generated {len([p for p in profiles if p])} agents in total")
        print(f"{'='*60}\n")
        
        return profiles
    
    def _print_generated_profile(self, entity_name: str, entity_type: str, profile: OasisAgentProfile):
        """Print the generated persona to the console in real time without truncation."""
        separator = "-" * 70
        
        # Build the full output without truncation
        topics_str = ', '.join(profile.interested_topics) if profile.interested_topics else 'None'
        
        output_lines = [
            f"\n{separator}",
            f"[Generated] {entity_name} ({entity_type})",
            f"{separator}",
            f"Username: {profile.user_name}",
            f"",
            f"[Bio]",
            f"{profile.bio}",
            f"",
            f"[Detailed Persona]",
            f"{profile.persona}",
            f"",
            f"[Core Attributes]",
            f"Age: {profile.age} | Gender: {profile.gender} | MBTI: {profile.mbti}",
            f"Profession: {profile.profession} | Country: {profile.country}",
            f"OPS: trust_government={profile.trust_government}, shame_sensitivity={profile.shame_sensitivity}, "
            f"primary_fear={profile.primary_fear}, influence_radius={profile.influence_radius}, "
            f"fb_intensity={profile.fb_intensity}, dialect={profile.dialect}, "
            f"income_stability={profile.income_stability}, rumour_amplifier={profile.rumour_amplifier}",
            f"Interested topics: {topics_str}",
            separator
        ]
        
        output = "\n".join(output_lines)
        
        # Print only to the console to avoid duplicate full-output logging
        print(output)
    
    def save_profiles(
        self,
        profiles: List[OasisAgentProfile],
        file_path: str,
        platform: str = "reddit"
    ):
        """
        Save profiles to a file using the correct format for the selected platform.

        OASIS platform format requirements:
        - Twitter: CSV
        - Reddit: JSON
        
        Args:
            profiles: Profile list
            file_path: File path
            platform: Platform type, `"reddit"` or `"twitter"`
        """
        if platform == "twitter":
            self._save_twitter_csv(profiles, file_path)
        else:
            self._save_reddit_json(profiles, file_path)
    
    def _save_twitter_csv(self, profiles: List[OasisAgentProfile], file_path: str):
        """
        Save Twitter profiles in CSV format to match official OASIS requirements.

        Required OASIS Twitter CSV fields:
        - `user_id`: user ID starting from 0 in CSV order
        - `name`: the user's real name
        - `username`: the username used by the system
        - `user_char`: detailed persona text injected into the LLM system prompt to guide agent behavior
        - `description`: a short public bio shown on the profile page

        Difference between `user_char` and `description`:
        - `user_char`: internal use only, becomes part of the LLM system prompt, and shapes how the agent thinks and acts
        - `description`: external display only, visible to other users
        """
        import csv
        
        # Ensure the file extension is `.csv`
        if not file_path.endswith('.csv'):
            file_path = file_path.replace('.json', '.csv')
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write the header required by OASIS
            headers = ['user_id', 'name', 'username', 'user_char', 'description']
            writer.writerow(headers)
            
            # Write data rows
            for idx, profile in enumerate(profiles):
                # `user_char`: full persona (`bio` + `persona` + OPS fields), used in the LLM system prompt
                user_char = profile.build_user_char()
                
                # `description`: short bio for external display
                description = profile.bio.replace('\n', ' ').replace('\r', ' ')
                
                row = [
                    idx,                    # user_id: sequential ID starting from 0
                    profile.name,           # name: real name
                    profile.user_name,      # username: username
                    user_char,              # user_char: full persona for internal LLM use
                    description             # description: short public-facing bio
                ]
                writer.writerow(row)
        
        logger.info(f"Saved {len(profiles)} Twitter profiles to {file_path} (OASIS CSV format)")
    
    def _normalize_gender(self, gender: Optional[str]) -> str:
        """
        Normalize the `gender` field to the English values required by OASIS.

        OASIS requires: `male`, `female`, or `other`
        """
        if not gender:
            return "other"
        
        gender_lower = gender.lower().strip()
        
        # Preserve accepted non-English input aliases without changing behavior
        gender_map = {
            "\u7537": "male",
            "\u5973": "female",
            "\u673a\u6784": "other",
            "\u5176\u4ed6": "other",
            # English values already supported
            "male": "male",
            "female": "female",
            "other": "other",
        }
        
        return gender_map.get(gender_lower, "other")
    
    def _save_reddit_json(self, profiles: List[OasisAgentProfile], file_path: str):
        """
        Save Reddit profiles in JSON format.

        Use the same structure as `to_reddit_format()` so OASIS can read it correctly.
        The `user_id` field is required because it is the key used by `OASIS agent_graph.get_agent()` for matching.

        Required fields:
        - `user_id`: user ID as an integer, used to match `poster_agent_id` in `initial_posts`
        - `username`: username
        - `name`: display name
        - `bio`: profile bio
        - `persona`: detailed persona
        - `age`: age as an integer
        - `gender`: `"male"`, `"female"`, or `"other"`
        - `mbti`: MBTI type
        - `country`: country
        """
        data = []
        for idx, profile in enumerate(profiles):
            # Use the same structure as `to_reddit_format()`
            item = {
                "user_id": profile.user_id if profile.user_id is not None else idx,  # Critical: `user_id` must be present
                "username": profile.user_name,
                "name": profile.name,
                "bio": profile.bio[:150] if profile.bio else f"{profile.name}",
                "persona": profile.persona or f"{profile.name} is a participant in social discussions.",
                "karma": profile.karma if profile.karma else 1000,
                "created_at": profile.created_at,
                # OASIS-required fields: ensure each one has a default value
                "age": profile.age if profile.age else 30,
                "gender": self._normalize_gender(profile.gender),
                "mbti": profile.mbti if profile.mbti else "ISTJ",
                "country": profile.country if profile.country else "China",
            }
            item.update(profile.ops_fields())
            
            # Optional fields
            if profile.profession:
                item["profession"] = profile.profession
            if profile.interested_topics:
                item["interested_topics"] = profile.interested_topics
            
            data.append(item)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(profiles)} Reddit profiles to {file_path} (JSON format including `user_id`)")
    
    # Keep the old method name as an alias for backward compatibility
    def save_profiles_to_json(
        self,
        profiles: List[OasisAgentProfile],
        file_path: str,
        platform: str = "reddit"
    ):
        """[Deprecated] Use `save_profiles()` instead."""
        logger.warning("`save_profiles_to_json` is deprecated; use `save_profiles()` instead")
        self.save_profiles(profiles, file_path, platform)

