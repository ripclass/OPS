"""
Ontology generation service.
API 1: analyze the text content and generate entity and relationship type definitions for social simulation.
"""

import json
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


# System prompt for ontology generation
ONTOLOGY_SYSTEM_PROMPT = """You are a professional knowledge-graph ontology design expert. Your task is to analyze the given text content and simulation requirements, then design entity types and relationship types suitable for **social media public-opinion simulation**.

**Important: you must output valid JSON only. Do not output anything else.**

## Core task background

We are building a **social media public-opinion simulation system**. In this system:
- Each entity is an "account" or "actor" that can speak, interact, and spread information on social media
- Entities influence one another, repost, comment, and respond
- We need to simulate how each party reacts during a public-opinion event and how information propagates

Therefore, **entities must be real-world actors that can genuinely speak and interact on social media**.

**Allowed entity categories**:
- Specific individuals, such as public figures, involved parties, opinion leaders, experts, scholars, or ordinary people
- Companies and businesses, including their official accounts
- Organizations and institutions, such as universities, associations, NGOs, or unions
- Government departments and regulatory bodies
- Media organizations, such as newspapers, TV stations, self-media outlets, and websites
- Social media platforms themselves
- Representatives of specific groups, such as alumni associations, fan communities, or rights-advocacy groups

**Disallowed entity categories**:
- Abstract concepts such as "public opinion", "emotion", or "trend"
- Topics or issues such as "academic integrity" or "education reform"
- Viewpoints or stances such as "supporters" or "opponents"

## Output format

Output JSON with the following structure:

```json
{
    "entity_types": [
        {
            "name": "Entity type name (English, PascalCase)",
            "description": "Short description (English, under 100 characters)",
            "attributes": [
                {
                    "name": "Attribute name (English, snake_case)",
                    "type": "text",
                    "description": "Attribute description"
                }
            ],
            "examples": ["Example entity 1", "Example entity 2"]
        }
    ],
    "edge_types": [
        {
            "name": "Relationship type name (English, UPPER_SNAKE_CASE)",
            "description": "Short description (English, under 100 characters)",
            "source_targets": [
                {"source": "Source entity type", "target": "Target entity type"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis of the text content (English)"
}
```

## Design guidelines (extremely important)

### 1. Entity type design - must be followed strictly

**Quantity requirement: output exactly 10 entity types**

**Hierarchy requirement (must include both specific types and fallback types)**:

Your 10 entity types must follow this structure:

A. **Fallback types (must be included, and must be the last 2 items in the list)**:
   - `Person`: Fallback type for any individual human. Use this when a person does not fit a more specific person type.
   - `Organization`: Fallback type for any organization. Use this when an organization does not fit a more specific organization type.

B. **Specific types (8 total, designed from the text)**:
   - Create more specific types for the main roles that appear in the text
   - Example: if the text describes an academic event, you might include `Student`, `Professor`, and `University`
   - Example: if the text describes a business event, you might include `Company`, `CEO`, and `Employee`

**Why fallback types are needed**:
- The text may include many kinds of people, such as school teachers, bystanders, or unnamed internet users
- If no specialized type fits them, they should fall under `Person`
- Likewise, small organizations or temporary groups should fall under `Organization`

**Design principles for specific types**:
- Identify frequently appearing or key role types from the text
- Each specific type should have clear boundaries and avoid overlap
- The `description` must clearly explain how this type differs from the fallback type

### 2. Relationship type design

- Quantity: 6 to 10
- Relationships should reflect real connections in social-media interaction
- Ensure the `source_targets` cover the entity types you define

### 3. Attribute design

- Each entity type should have 1 to 3 key attributes
- **Important**: attribute names cannot use reserved system fields such as `name`, `uuid`, `group_id`, `created_at`, or `summary`
- Recommended names include `full_name`, `title`, `role`, `position`, `location`, and `description`

## Entity type references

**Person-like types (specific)**:
- Student
- Professor
- Journalist
- Celebrity
- Executive
- Official
- Lawyer
- Doctor

**Person-like fallback type**:
- Person: any individual human not covered by the more specific types above

**Organization-like types (specific)**:
- University
- Company
- GovernmentAgency
- MediaOutlet
- Hospital
- School
- NGO

**Organization-like fallback type**:
- Organization: any organization not covered by the more specific types above

## Relationship type references

- WORKS_FOR: employed by
- STUDIES_AT: studies at
- AFFILIATED_WITH: affiliated with
- REPRESENTS: represents
- REGULATES: regulates
- REPORTS_ON: reports on
- COMMENTS_ON: comments on
- RESPONDS_TO: responds to
- SUPPORTS: supports
- OPPOSES: opposes
- COLLABORATES_WITH: collaborates with
- COMPETES_WITH: competes with
"""


class OntologyGenerator:
    """
    Ontology generator.
    Analyzes text content and generates entity and relationship type definitions.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate the ontology definition.
        
        Args:
            document_texts: List of document texts
            simulation_requirement: Simulation requirement description
            additional_context: Additional context
            
        Returns:
            Ontology definition, including `entity_types`, `edge_types`, and related fields
        """
        # Build the user message
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        # Validate and post-process the result
        result = self._validate_and_process(result)
        
        return result
    
    # Maximum text length sent to the LLM (50,000 characters)
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """Build the user message."""
        
        # Merge the text
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # If the text exceeds 50,000 characters, truncate it.
        # This affects only the content passed to the LLM, not graph construction.
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...(Original text length: {original_length} characters. Only the first {self.MAX_TEXT_LENGTH_FOR_LLM} characters were used for ontology analysis)..."

        message = f"""## Simulation Requirement

{simulation_requirement}

## Document Content

{combined_text}
"""
        
        if additional_context:
            message += f"""
## Additional Notes

{additional_context}
"""

        message += """
Based on the content above, design entity types and relationship types suitable for social public-opinion simulation.

**Rules that must be followed**:
1. You must output exactly 10 entity types
2. The last 2 must be the fallback types `Person` and `Organization`
3. The first 8 must be specific types designed from the text content
4. All entity types must be real-world actors that can speak publicly; they cannot be abstract concepts
5. Attribute names cannot use reserved fields such as `name`, `uuid`, or `group_id`; use alternatives such as `full_name` and `org_name`
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and post-process the result."""
        
        # Ensure required fields exist
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # Validate entity types
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # Ensure descriptions do not exceed 100 characters
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # Validate edge types
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API limits: at most 10 custom entity types and 10 custom edge types
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        # Fallback type definitions
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # Check whether fallback types already exist
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # Fallback types that still need to be added
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # If adding them would exceed 10, remove some existing types first
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # Compute how many need to be removed
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # Remove from the end, preserving earlier and likely more important specific types
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # Add the fallback types
            result["entity_types"].extend(fallbacks_to_add)
        
        # Final defensive limit enforcement
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        Convert the ontology definition into Python code, similar to `ontology.py`.
        
        Args:
            ontology: Ontology definition
            
        Returns:
            Python code as a string
        """
        code_lines = [
            '"""',
            'Custom entity type definitions',
            'Automatically generated by MiroFish for social public-opinion simulation',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== Entity Type Definitions ==============',
            '',
        ]
        
        # Generate entity types
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== Relationship Type Definitions ==============')
        code_lines.append('')
        
        # Generate relationship types
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # Convert to a PascalCase class name
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # Generate type dictionaries
        code_lines.append('# ============== Type Configuration ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # Generate the edge `source_targets` mapping
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)

