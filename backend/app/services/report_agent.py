"""
Report Agent service
Using LangChain + Zep to implement simulation report generation in ReACT mode

Function:
1. Generate reports based on simulation requirements and Zep map information
2. Plan the directory structure first, and then generate it in segments
3. Each paragraph adopts ReACT multiple rounds of thinking and reflection mode
4. Support dialogue with users and autonomously call search tools during the dialogue
"""

import os
import json
import time
import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from .zep_tools import (
    ZepToolsService, 
    SearchResult, 
    InsightForgeResult, 
    PanoramaResult,
    InterviewResult
)

logger = get_logger('ops.report_agent')


class ReportLogger:
    """
    Report Agent Detailed Logger
    
    Generate agent_log.jsonl file in the report folder to record detailed actions of each step.
    Each row is a complete JSON object, including timestamp, action type, details, etc.
    """
    
    def __init__(self, report_id: str):
        """
        Initialize the logger
        
        Args:
            report_id: report ID, used to determine the log file path
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'agent_log.jsonl'
        )
        self.start_time = datetime.now()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Make sure the directory where the log file is located exists"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _get_elapsed_time(self) -> float:
        """Get the elapsed time from start to now (seconds)"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def log(
        self, 
        action: str, 
        stage: str,
        details: Dict[str, Any],
        section_title: str = None,
        section_index: int = None
    ):
        """
        record a log
        
        Args:
            action: action type, such as 'start', 'tool_call', 'llm_response', 'section_complete', etc.
            stage: current stage, such as 'planning', 'generating', 'completed'
            details: Dictionary of details, not truncated
            section_title: current section title (optional)
            section_index: current section index (optional)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(self._get_elapsed_time(), 2),
            "report_id": self.report_id,
            "action": action,
            "stage": stage,
            "section_title": section_title,
            "section_index": section_index,
            "details": details
        }
        
        # Append writing to JSONL file
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_start(self, simulation_id: str, graph_id: str, simulation_requirement: str):
        """Logging report generation begins"""
        self.log(
            action="report_start",
            stage="pending",
            details={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "simulation_requirement": simulation_requirement,
                "message": "Report generation task starts"
            }
        )
    
    def log_planning_start(self):
        """Record Outline Planning Begins"""
        self.log(
            action="planning_start",
            stage="planning",
            details={"message": "Start planning your report outline"}
        )
    
    def log_planning_context(self, context: Dict[str, Any]):
        """Record contextual information obtained during planning"""
        self.log(
            action="planning_context",
            stage="planning",
            details={
                "message": "Get simulation context information",
                "context": context
            }
        )
    
    def log_planning_complete(self, outline_dict: Dict[str, Any]):
        """Record outline planning completed"""
        self.log(
            action="planning_complete",
            stage="planning",
            details={
                "message": "Outline planning completed",
                "outline": outline_dict
            }
        )
    
    def log_section_start(self, section_title: str, section_index: int):
        """Record chapter generation starts"""
        self.log(
            action="section_start",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={"message": f"Start generating chapters:{section_title}"}
        )
    
    def log_react_thought(self, section_title: str, section_index: int, iteration: int, thought: str):
        """Document your ReACT thought process"""
        self.log(
            action="react_thought",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "thought": thought,
                "message": f"ReACT No.{iteration}round of thinking"
            }
        )
    
    def log_tool_call(
        self, 
        section_title: str, 
        section_index: int,
        tool_name: str, 
        parameters: Dict[str, Any],
        iteration: int
    ):
        """Logging tool calls"""
        self.log(
            action="tool_call",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "parameters": parameters,
                "message": f"Call tool:{tool_name}"
            }
        )
    
    def log_tool_result(
        self,
        section_title: str,
        section_index: int,
        tool_name: str,
        result: str,
        iteration: int
    ):
        """Record tool call results (complete content, not truncated)"""
        self.log(
            action="tool_result",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "result": result,  # Complete result, no truncation
                "result_length": len(result),
                "message": f"tool{tool_name} Return results"
            }
        )
    
    def log_llm_response(
        self,
        section_title: str,
        section_index: int,
        response: str,
        iteration: int,
        has_tool_calls: bool,
        has_final_answer: bool
    ):
        """Logging LLM response (full content, not truncated)"""
        self.log(
            action="llm_response",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "response": response,  # Complete response, no truncation
                "response_length": len(response),
                "has_tool_calls": has_tool_calls,
                "has_final_answer": has_final_answer,
                "message": f"LLM response (tool call:{has_tool_calls}, final answer:{has_final_answer})"
            }
        )
    
    def log_section_content(
        self,
        section_title: str,
        section_index: int,
        content: str,
        tool_calls_count: int
    ):
        """Record chapter content generation is completed (only record content, does not mean the entire chapter is completed)"""
        self.log(
            action="section_content",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": content,  # Complete content, no truncation
                "content_length": len(content),
                "tool_calls_count": tool_calls_count,
                "message": f"chapter{section_title} Content generation completed"
            }
        )
    
    def log_section_full_complete(
        self,
        section_title: str,
        section_index: int,
        full_content: str
    ):
        """
        Record chapter generation completed

        The front end should listen to this log to determine whether a chapter is actually completed and obtain the complete content
        """
        self.log(
            action="section_complete",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": full_content,
                "content_length": len(full_content),
                "message": f"chapter{section_title} Generation completed"
            }
        )
    
    def log_report_complete(self, total_sections: int, total_time_seconds: float):
        """Record report generation completed"""
        self.log(
            action="report_complete",
            stage="completed",
            details={
                "total_sections": total_sections,
                "total_time_seconds": round(total_time_seconds, 2),
                "message": "Report generation completed"
            }
        )
    
    def log_error(self, error_message: str, stage: str, section_title: str = None):
        """Log errors"""
        self.log(
            action="error",
            stage=stage,
            section_title=section_title,
            section_index=None,
            details={
                "error": error_message,
                "message": f"An error occurred:{error_message}"
            }
        )


class ReportConsoleLogger:
    """
    Report Agent console logger
    
    Write console-style logs (INFO, WARNING, etc.) to the console_log.txt file in the reports folder.
    These logs, unlike agent_log.jsonl, are console output in plain text format.
    """
    
    def __init__(self, report_id: str):
        """
        Initialize the console logger
        
        Args:
            report_id: report ID, used to determine the log file path
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'console_log.txt'
        )
        self._ensure_log_file()
        self._file_handler = None
        self._setup_file_handler()
    
    def _ensure_log_file(self):
        """Make sure the directory where the log file is located exists"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _setup_file_handler(self):
        """Set up the file processor to write logs to files at the same time"""
        import logging
        
        # Create file handler
        self._file_handler = logging.FileHandler(
            self.log_file_path,
            mode='a',
            encoding='utf-8'
        )
        self._file_handler.setLevel(logging.INFO)
        
        # Use the same concise format as the console
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self._file_handler.setFormatter(formatter)
        
        # Added to report_agent related logger
        loggers_to_attach = [
            'ops.report_agent',
            'ops.zep_tools',
        ]
        
        for logger_name in loggers_to_attach:
            target_logger = logging.getLogger(logger_name)
            # Avoid duplicate additions
            if self._file_handler not in target_logger.handlers:
                target_logger.addHandler(self._file_handler)
    
    def close(self):
        """Close the file handler and remove it from the logger"""
        import logging
        
        if self._file_handler:
            loggers_to_detach = [
                'ops.report_agent',
                'ops.zep_tools',
            ]
            
            for logger_name in loggers_to_detach:
                target_logger = logging.getLogger(logger_name)
                if self._file_handler in target_logger.handlers:
                    target_logger.removeHandler(self._file_handler)
            
            self._file_handler.close()
            self._file_handler = None
    
    def __del__(self):
        """Make sure to close the file handler on destruction"""
        self.close()


class ReportStatus(str, Enum):
    """Report status"""
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportSection:
    """Report Chapter"""
    title: str
    content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content
        }

    def to_markdown(self, level: int = 2) -> str:
        """Convert to Markdown format"""
        md = f"{'#' * level} {self.title}\n\n"
        if self.content:
            md += f"{self.content}\n\n"
        return md


@dataclass
class ReportOutline:
    """Report outline"""
    title: str
    summary: str
    sections: List[ReportSection]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections]
        }
    
    def to_markdown(self) -> str:
        """Convert to Markdown format"""
        md = f"# {self.title}\n\n"
        md += f"> {self.summary}\n\n"
        for section in self.sections:
            md += section.to_markdown()
        return md


@dataclass
class Report:
    """full report"""
    report_id: str
    simulation_id: str
    graph_id: str
    simulation_requirement: str
    status: ReportStatus
    outline: Optional[ReportOutline] = None
    markdown_content: str = ""
    created_at: str = ""
    completed_at: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "simulation_id": self.simulation_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "status": self.status.value,
            "outline": self.outline.to_dict() if self.outline else None,
            "markdown_content": self.markdown_content,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Prompt template constant
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# â”€â”€ Tool description â”€â”€

TOOL_DESC_INSIGHT_FORGE = """\
[Deep Insight Search - Powerful Search Tool]
This is our powerful search function, designed for in-depth analysis. It will:
1. Automatically decompose your problem into multiple sub-problems
2. Retrieve information in simulation maps from multiple dimensions
3. Integrate the results of semantic search, entity analysis, and relationship chain tracking
4. Return the most comprehensive and in-depth search content

ã€Usage Scenarioã€‘
- Need to analyze a topic in depth
- Need to understand multiple aspects of the incident
- Need to obtain rich materials to support the report chapters

ã€Return to contentã€‘
- Original text of relevant facts (can be quoted directly)
- Core entity insights
-Relationship chain analysis"""

TOOL_DESC_PANORAMA_SEARCH = """\
[Breadth Search - Get a Full View]
This tool is used to obtain a complete picture of the simulation results and is particularly suitable for understanding the evolution of events. It will:
1. Get all relevant nodes and relationships
2. Distinguish between currently valid facts and historical/expired facts
3. Help you understand how public opinion evolves

ã€Usage Scenarioã€‘
- Need to understand the complete development of the incident
- Need to compare changes in public opinion at different stages
- Need to obtain comprehensive entity and relationship information

ã€Return to contentã€‘
- Current valid facts (simulate the latest results)
- Historical/expired facts (evolution records)
- All entities involved"""

TOOL_DESC_QUICK_SEARCH = """\
[Simple search - quick search]
A lightweight fast retrieval tool suitable for simple and direct information query.

ã€Usage Scenarioã€‘
- Need to find specific information quickly
- Need to verify a fact
- Simple information retrieval

ã€Return to contentã€‘
- List of facts most relevant to the query"""

TOOL_DESC_INTERVIEW_AGENTS = """\
[In-depth interview - real agent interview (dual platform)]
Call the interview API of the OASIS simulation environment to conduct a real interview with the running simulation Agent!
This is not an LLM simulation, but calling the real interview interface to obtain the original answers of the simulated agent.
By default, interviews will be conducted simultaneously on both Twitter and Reddit to obtain a more comprehensive view.

Functional flow:
1. Automatically read character files and understand all simulated Agents
2. Intelligently select the Agent most relevant to the interview topic (such as students, media, officials, etc.)
3. Automatically generate interview questions
4. Call the /api/simulation/interview/batch interface to conduct real interviews on dual platforms
5. Integrate all interview results and provide multi-perspective analysis

ã€Usage Scenarioã€‘
- Need to understand the views of events from different rolesâ€™ perspectives (What do students think? What do the media think? What do officials say?)
- Need to collect opinions and positions from multiple parties
- Need to obtain the real answer of the simulated Agent (from the OASIS simulation environment)
- I want to make the report more vivid and include "Interview Record"

ã€Return to contentã€‘
- Identity information of the agent being interviewed
- Interview answers from each Agent on Twitter and Reddit
- Key quotes (can be quoted directly)
- Interview summaries and point of view comparisons

[Important] The OASIS simulation environment needs to be running to use this function!"""

# â”€â”€Outline planning promptâ”€â”€

PLAN_SYSTEM_PROMPT = """\
You are an expert in writing "future prediction reports" and have a "God's perspective" on the simulated world - you can gain insight into the behavior, speech and interaction of every agent in the simulation.

ã€Core Conceptã€‘
We build a simulation world and inject specific "simulation requirements" as variables into it. The evolution of the simulated world is a prediction of what may happen in the future. What you are observing is not "experimental data" but "a preview of the future".

ã€Your missionã€‘
Write a "Future Forecast Report" and answer:
1. What happens in the future under the conditions we set?
2. How do various Agents (people) react and act?
3. What future trends and risks does this simulation reveal that are worthy of attention?

[Report positioning]
- âœ… This is a simulation-based future prediction report that reveals "what will happen in the future if this happens"
- âœ… Focus on predicting results: event trends, group reactions, emerging phenomena, potential risks
- âœ… The words and deeds of the Agent in the simulated world are predictions of future crowd behavior.
- âŒ Not an analysis of real-world conditions
- âŒ This is not a general summary of public opinion.

[Limited number of chapters]
- Minimum 2 chapters, maximum 5 chapters
- No sub-chapters are needed, each chapter directly writes the complete content
- The content should be refined and focused on core predictions and findings
- The chapter structure is designed by you based on the prediction results

Please output the report outline in JSON format, the format is as follows:
{
    "title": "Report title",
    "summary": "Report summary (one sentence summarizing the core prediction findings)",
    "sections": [
        {
            "title": "Chapter title",
            "description": "Chapter content description"
        }
    ]
}

Note: The sections array has a minimum of 2 and a maximum of 5 elements!"""

PLAN_USER_PROMPT_TEMPLATE = """\
[Prediction scene settings]
Variables we inject into the simulation world (simulation requirements): {simulation_requirement}

[Simulated World Scale]
- Number of entities participating in the simulation: {total_nodes}
- Number of relationships generated between entities: {total_edges}
- Entity type distribution: {entity_types}
- Number of active Agents: {total_entities}

[Samples of some future facts predicted by simulation]
{related_facts_json}

Please look at this future preview from a "God's perspective":
1. Under the conditions we set, what will the future look like?
2. How do various groups of people (Agents) react and act?
3. What future trends does this simulation reveal that are worthy of attention?

Based on the prediction results, design the most appropriate report chapter structure.

[Remind again] Number of report chapters: minimum 2, maximum 5. The content should be refined and focused on core predictions and findings."""

# â”€â”€Chapter generation promptâ”€â”€

SECTION_SYSTEM_PROMPT_TEMPLATE = """\
You are a future-forecast report writer and are drafting one chapter of the report.

Report title: {report_title}
Report summary: {report_summary}
Forecast scenario (simulation requirement): {simulation_requirement}

Chapter currently being written: {section_title}

================================================================
[Core Concept]
================================================================

The simulated world is a preview of the future. We inject the scenario into the simulation world,
and the agents' behavior and interactions are predictions of future crowd behavior.

Your task is to:
- reveal what is likely to happen under the scenario
- predict how different kinds of people or organizations will react
- identify trends, risks, and opportunities worth attention

Do not write this as a retrospective analysis of real-world events.
Focus on what is likely to happen next in the simulated future.

================================================================
[Mandatory Rules]
================================================================

1. [You must use tools to observe the simulated world]
   - All report content must come from events that occurred in the simulated world
   - Do not use your own outside knowledge to invent findings
   - Call tools at least 3 times per chapter and at most 5 times

2. [Quote what the agents actually say or do]
   - Agent speech and behavior are the evidence for predicted public response
   - Present important evidence in quotation format, for example:
     > "A specific group is likely to say: original content..."

3. [Keep language consistent]
   - Tool output may contain multilingual or mixed-language material
   - Write the chapter in the report language requested by the user; default to English
   - When quoting material in another language, translate it into the report language while preserving the meaning
   - Apply this rule to both narrative text and block quotes

4. [Represent the simulation faithfully]
   - Report content must reflect the simulated future exactly as observed
   - Do not add facts that do not appear in the simulation
   - If information is missing, say so directly

================================================================
[Format Rules]
================================================================

[A chapter is the smallest unit of content]
- Do not use Markdown headings such as #, ##, ###, or ####
- Do not repeat the chapter title at the start of the content
- The system inserts chapter titles automatically
- Use bold text, paragraph breaks, quotes, and lists to structure the chapter

[Correct example]
```
This chapter examines how the scenario gains momentum across the network.

**Initial trigger**

The first visible reaction comes from local community pages:

> "People are already asking whether the price jump is final."

**Amplification**

Discussion then accelerates through peer-to-peer sharing:

- neighborhood groups repeat the warning
- rumor-heavy accounts add emotional framing
```

[Incorrect example]
```
## Executive Summary
### First stage
#### Detailed analysis

This chapter examines...
```

================================================================
[Available Search Tools] (call tools 3-5 times per chapter)
================================================================

{tools_description}

[Tool usage suggestions - use a mix of different tools]
- insight_forge: deep multi-angle analysis across facts and relationships
- panorama_search: broad search across timeline, entities, and evolution
- quick_search: fast verification of a specific point
- interview_agents: direct agent interviews for first-person reactions

================================================================
[Workflow]
================================================================

In each reply you may do only one of the following:

Option A - Call a tool
Print your reasoning, then call exactly one tool using:
<tool_call>
{{"name": "tool_name", "parameters": {{"param": "value"}}}}
</tool_call>

Option B - Output final content
After you have enough evidence, output the chapter content starting with "Final Answer:".

Strictly prohibited:
- including both a tool call and Final Answer in one reply
- fabricating tool results
- calling more than one tool in a single reply

================================================================
[Chapter Content Requirements]
================================================================

1. Content must be based on simulation data returned by tools
2. Use concrete quotes from the simulation where they add evidence
3. Use Markdown formatting without headings:
   - use **bold** for emphasis instead of section headings
   - use lists to organize key points
   - use blank lines between paragraphs
4. Quote formatting:
   - place quotes in their own paragraphs with a blank line before and after
   - do not bury quotes inside a normal paragraph
5. Keep the chapter logically consistent with the rest of the report
6. Avoid repetition with completed chapters
7. Do not add headings; if you need internal structure, use **bold** labels instead"""

SECTION_USER_PROMPT_TEMPLATE = """\
Completed chapter content (read carefully to avoid repetition):
{previous_content}

================================================================
[Current task] Write the chapter: {section_title}
================================================================

[Important reminders]
1. Read the completed chapters above and avoid repeating them
2. You must call tools before drafting the chapter
3. Use a mix of tools rather than relying on only one
4. All report content must come from retrieved simulation evidence

[Format warning]
- Do not write any Markdown heading (#, ##, ###, ####)
- Do not start the chapter by repeating "{section_title}"
- Chapter titles are added automatically by the system
- Write the chapter body directly and use **bold** instead of headings

Please begin:
1. Decide what information you need
2. Call a tool to retrieve simulation evidence
3. After enough evidence is collected, output Final Answer with plain text only"""

# -- ReACT in-loop message template --

REACT_OBSERVATION_TEMPLATE = """\
Observation (retrieval results):

=== tool {tool_name} returned ===
{result}

=================================
Tools called: {tool_calls_count}/{max_tool_calls} (used: {used_tools_str}) {unused_hint}
- If the evidence is sufficient, output the chapter content starting with "Final Answer:"
- If more evidence is needed, call another tool
================================="""

REACT_INSUFFICIENT_TOOLS_MSG = (
    "[Note] You only called the tool {tool_calls_count} times, at least {min_tool_calls} times are required."
    "Please call the tool again to obtain more simulation data, and then output the Final Answer. {unused_hint}"
)

REACT_INSUFFICIENT_TOOLS_MSG_ALT = (
    "Currently only {tool_calls_count} tool calls have been made, at least {min_tool_calls} are required."
    "Please call the tool to obtain simulation data. {unused_hint}"
)

REACT_TOOL_LIMIT_MSG = (
    "The number of tool calls has reached the upper limit ({tool_calls_count}/{max_tool_calls}), and the tool can no longer be called."
    'Please immediately output the chapter content starting with "Final Answer:" based on the information you have obtained.'
)

REACT_UNUSED_TOOLS_HINT = "\\nðŸ’¡ You have not used: {unused_list}, it is recommended to try different tools to obtain multi-angle information"

REACT_FORCE_FINAL_MSG = "The tool calling limit has been reached, please directly output Final Answer: and generate chapter content."

# â”€â”€ Chat prompt â”€â”€

CHAT_SYSTEM_PROMPT_TEMPLATE = """\
You are a simple and efficient simulation prediction assistant.

ã€backgroundã€‘
Prediction condition: {simulation_requirement}

[Generated analysis report]
{report_content}

ã€ruleã€‘
1. Prioritize answering questions based on the above report content
2. Answer the question directly and avoid lengthy thinking and discussion.
3. Only call the tool to retrieve more data if the report content is not enough to answer the question
4. Answers should be concise, clear and organized

[Available tools] (only used when needed, called 1-2 times at most)
{tools_description}

[Tool calling format]
<tool_call>
{{"name": "Tool name", "parameters": {{"Parameter name": "Parameter value"}}}}
</tool_call>

[Answer style]
- Be concise and direct, donâ€™t make lengthy statements
- Quote key content using the > format
- Give conclusions first, then explain the reasons"""

CHAT_OBSERVATION_SUFFIX = "\\n\\nPlease answer the question concisely."


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ReportAgent main class
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ReportAgent:
    """
    Report Agent - Simulate report generation agent

    Adopt ReACT (Reasoning + Acting) mode:
    1. Planning stage: analyze simulation requirements and plan the report directory structure
    2. Generation phase: Generate content chapter by chapter, and each chapter can call the tool multiple times to obtain information.
    3. Reflection stage: Check content for completeness and accuracy
    """
    
    # Maximum number of tool calls (per chapter)
    MAX_TOOL_CALLS_PER_SECTION = 5
    
    # Maximum number of reflection rounds
    MAX_REFLECTION_ROUNDS = 3
    
    # Maximum number of tool calls in a conversation
    MAX_TOOL_CALLS_PER_CHAT = 2
    
    def __init__(
        self, 
        graph_id: str,
        simulation_id: str,
        simulation_requirement: str,
        llm_client: Optional[LLMClient] = None,
        zep_tools: Optional[ZepToolsService] = None
    ):
        """
        Initialize Report Agent
        
        Args:
            graph_id: graph ID
            simulation_id: simulation ID
            simulation_requirement: simulation requirement description
            llm_client: LLM client (optional)
            zep_tools: Zep tool service (optional)
        """
        self.graph_id = graph_id
        self.simulation_id = simulation_id
        self.simulation_requirement = simulation_requirement
        self.ops_metadata = self._parse_ops_metadata(simulation_requirement)
        self.ops_population_params: Dict[str, Any] = {}
        try:
            from .simulation_manager import SimulationManager

            state = SimulationManager().get_simulation(simulation_id)
            if state and getattr(state, "ops_population_params", None):
                self.ops_population_params = dict(state.ops_population_params or {})
        except Exception as exc:
            logger.warning(f"Failed to read OPS population params for report {simulation_id}: {exc}")

        if self.ops_population_params and not self.ops_metadata:
            origin_country = self.ops_population_params.get("origin_country")
            origin_countries = self.ops_population_params.get("origin_countries") or []
            audience_region = self.ops_population_params.get("audience_region")
            corridor = self.ops_population_params.get("corridor")
            self.ops_metadata = {
                "run type": str(self.ops_population_params.get("run_type") or "Domestic"),
                "origin country": str(origin_country or (origin_countries[0] if origin_countries else "South Asia")),
                "segments": ", ".join(self.ops_population_params.get("segments") or []),
                "target agents": str(self.ops_population_params.get("n_agents") or ""),
                "requested outputs": ", ".join(self.ops_population_params.get("requested_outputs") or []),
            }
            if audience_region:
                self.ops_metadata["audience region"] = str(audience_region)
            if corridor:
                self.ops_metadata["corridor"] = str(corridor)

        self.is_ops_report = bool(self.ops_metadata or self.ops_population_params)
        self.fast_report_mode = self.is_ops_report
        
        self.llm = llm_client or LLMClient()
        self.zep_tools = zep_tools or ZepToolsService()
        
        # Tool definition
        self.tools = self._define_tools()
        
        # Logger (initialized in generate_report)
        self.report_logger: Optional[ReportLogger] = None
        # Console logger (initialized in generate_report)
        self.console_logger: Optional[ReportConsoleLogger] = None
        
        logger.info(f"ReportAgent initialization completed: graph_id={graph_id}, simulation_id={simulation_id}")
    
    def _parse_ops_metadata(self, text: str) -> Dict[str, str]:
        """Parse the OPS metadata block embedded in the simulation requirement."""
        if not text or "[OPS Wizard Metadata]" not in text:
            return {}

        metadata: Dict[str, str] = {}
        pattern = re.compile(
            r"\[OPS Wizard Metadata\](.*?)\[/OPS Wizard Metadata\]",
            re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            return {}

        for raw_line in match.group(1).splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
        return metadata

    def _extract_primary_scenario_text(self) -> str:
        """Return the human scenario text without OPS metadata."""
        if "Scenario:" in self.simulation_requirement:
            return self.simulation_requirement.split("Scenario:", 1)[1].strip()
        return self.simulation_requirement.strip()

    def _get_fast_section_tool_names(self, section_index: int) -> List[str]:
        """Use lightweight tools for OPS preview reports."""
        if section_index <= 1:
            return ["quick_search", "panorama_search"]
        return ["panorama_search", "quick_search"]

    def _build_ops_fast_outline(self) -> ReportOutline:
        """Build a deterministic short outline for OPS runs."""
        scenario = self._extract_primary_scenario_text() or "South Asia scenario outlook"
        origin_country = self.ops_metadata.get("origin country", "South Asia")
        run_type = self.ops_metadata.get("run type", "Domestic")
        segments = self.ops_metadata.get("segments", "selected segments")

        compact_title = scenario.rstrip(" ?.")
        if len(compact_title) > 72:
            compact_title = compact_title[:72].rstrip() + "..."
        title = f"OPS Forecast Report: {compact_title}"

        summary = (
            f"This report forecasts how {segments.lower()} in {origin_country} may respond to the "
            f"scenario over the next rounds of the simulation."
        )

        if run_type.lower() == "diaspora":
            sections = [
                ReportSection(title="Immediate Diaspora Reaction"),
                ReportSection(title="Network Spillover and Pressure Risks"),
            ]
        elif run_type.lower() == "corridor-based":
            sections = [
                ReportSection(title="Corridor Reaction and Remittance Pressure"),
                ReportSection(title="Spillover Risks and Likely Next Moves"),
            ]
        elif run_type.lower() == "regional multi-country":
            sections = [
                ReportSection(title="Country-Level Reaction Patterns"),
                ReportSection(title="Regional Spillover and Escalation Risks"),
            ]
        else:
            sections = [
                ReportSection(title="Immediate Public Reaction"),
                ReportSection(title="Amplification Risks and Likely Next Moves"),
            ]

        return ReportOutline(title=title, summary=summary, sections=sections)
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available tools"""
        return {
            "insight_forge": {
                "name": "insight_forge",
                "description": TOOL_DESC_INSIGHT_FORGE,
                "parameters": {
                    "query": "A question or topic you would like to analyze in depth",
                    "report_context": "The context of the current report chapter (optional, helps generate more precise sub-questions)"
                }
            },
            "panorama_search": {
                "name": "panorama_search",
                "description": TOOL_DESC_PANORAMA_SEARCH,
                "parameters": {
                    "query": "Search query for relevance ranking",
                    "include_expired": "Whether to include expired/historical content (default True)"
                }
            },
            "quick_search": {
                "name": "quick_search",
                "description": TOOL_DESC_QUICK_SEARCH,
                "parameters": {
                    "query": "Search query string",
                    "limit": "Number of results returned (optional, default 10)"
                }
            },
            "interview_agents": {
                "name": "interview_agents",
                "description": TOOL_DESC_INTERVIEW_AGENTS,
                "parameters": {
                    "interview_topic": "Interview topic or description of needs (for example: 'Understand how low-income households may react to a 40% rice price increase')",
                    "max_agents": "Maximum number of agents to interview (optional, default 5, maximum 10)"
                }
            }
        }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any], report_context: str = "") -> str:
        """
        Execute tool call
        
        Args:
            tool_name: tool name
            parameters: tool parameters
            report_context: report context (for InsightForge)
            
        Returns:
            Tool execution results (text format)
        """
        logger.info(f"Execution tools:{tool_name}, parameters:{parameters}")
        
        try:
            if tool_name == "insight_forge":
                query = parameters.get("query", "")
                ctx = parameters.get("report_context", "") or report_context
                result = self.zep_tools.insight_forge(
                    graph_id=self.graph_id,
                    query=query,
                    simulation_requirement=self.simulation_requirement,
                    report_context=ctx
                )
                return result.to_text()
            
            elif tool_name == "panorama_search":
                # Breadth search - get the whole picture
                query = parameters.get("query", "")
                include_expired = parameters.get("include_expired", True)
                if isinstance(include_expired, str):
                    include_expired = include_expired.lower() in ['true', '1', 'yes']
                result = self.zep_tools.panorama_search(
                    graph_id=self.graph_id,
                    query=query,
                    include_expired=include_expired
                )
                return result.to_text()
            
            elif tool_name == "quick_search":
                # Simple search - quick retrieval
                query = parameters.get("query", "")
                limit = parameters.get("limit", 10)
                if isinstance(limit, str):
                    limit = int(limit)
                result = self.zep_tools.quick_search(
                    graph_id=self.graph_id,
                    query=query,
                    limit=limit
                )
                return result.to_text()
            
            elif tool_name == "interview_agents":
                # In-depth interview - call the real OASIS interview API to obtain the simulated Agent's answers (dual platforms)
                interview_topic = parameters.get("interview_topic", parameters.get("query", ""))
                max_agents = parameters.get("max_agents", 5)
                if isinstance(max_agents, str):
                    max_agents = int(max_agents)
                max_agents = min(max_agents, 10)
                result = self.zep_tools.interview_agents(
                    simulation_id=self.simulation_id,
                    interview_requirement=interview_topic,
                    simulation_requirement=self.simulation_requirement,
                    max_agents=max_agents
                )
                return result.to_text()
            
            # ========== Backward compatibility with old tools (internal redirect to new tools) ==========
            
            elif tool_name == "search_graph":
                # Redirect to quick_search
                logger.info("search_graph redirected to quick_search")
                return self._execute_tool("quick_search", parameters, report_context)
            
            elif tool_name == "get_graph_statistics":
                result = self.zep_tools.get_graph_statistics(self.graph_id)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_entity_summary":
                entity_name = parameters.get("entity_name", "")
                result = self.zep_tools.get_entity_summary(
                    graph_id=self.graph_id,
                    entity_name=entity_name
                )
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_simulation_context":
                # Redirect to insight_forge since it's more powerful
                logger.info("get_simulation_context redirected to insight_forge")
                query = parameters.get("query", self.simulation_requirement)
                return self._execute_tool("insight_forge", {"query": query}, report_context)
            
            elif tool_name == "get_entities_by_type":
                entity_type = parameters.get("entity_type", "")
                nodes = self.zep_tools.get_entities_by_type(
                    graph_id=self.graph_id,
                    entity_type=entity_type
                )
                result = [n.to_dict() for n in nodes]
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            else:
                return f"Unknown tool:{tool_name}. Please use one of the following tools: insight_forge, panorama_search, quick_search"
                
        except Exception as e:
            logger.error(f"Tool execution failed:{tool_name}, mistake:{str(e)}")
            return f"Tool execution failed:{str(e)}"
    
    # A collection of legal tool names for verification when parsing bare JSON
    VALID_TOOL_NAMES = {"insight_forge", "panorama_search", "quick_search", "interview_agents"}

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from LLM responses

        Supported formats (by priority):
        1. <tool_call>{"name": "tool_name", "parameters": {...}}</tool_call>
        2. Naked JSON (the response as a whole or a single line is a tool calling JSON)
        """
        tool_calls = []

        # Format 1: XML style (standard format)
        xml_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        for match in re.finditer(xml_pattern, response, re.DOTALL):
            try:
                call_data = json.loads(match.group(1))
                tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        if tool_calls:
            return tool_calls

        # Format 2: Keep it secret - LLM directly outputs bare JSON (without <tool_call> tag)
        # Only try when format 1 is not matched to avoid mismatching JSON in the body
        stripped = response.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            try:
                call_data = json.loads(stripped)
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
                    return tool_calls
            except json.JSONDecodeError:
                pass

        # Response may contain think text + bare JSON, try to extract last JSON object
        json_pattern = r'(\{"(?:name|tool)"\s*:.*?\})\s*$'
        match = re.search(json_pattern, stripped, re.DOTALL)
        if match:
            try:
                call_data = json.loads(match.group(1))
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        return tool_calls

    def _extract_final_answer(self, response: Optional[str]) -> str:
        """Extract the last usable Final Answer block from an LLM response."""
        if not response:
            return ""

        text = str(response).strip()
        if not text:
            return ""

        if "Final Answer:" in text:
            parts = [part.strip() for part in text.split("Final Answer:") if part.strip()]
            candidate = parts[-1] if parts else ""
        else:
            candidate = text

        # Remove any tool-call XML that may have leaked into the final answer body.
        candidate = re.sub(r'<tool_call>.*?</tool_call>', '', candidate, flags=re.DOTALL).strip()
        return candidate

    def _is_valid_tool_call(self, data: dict) -> bool:
        """Verify whether the parsed JSON is a legal tool call"""
        # Supports two key names: {"name": ..., "parameters": ...} and {"tool": ..., "params": ...}
        tool_name = data.get("name") or data.get("tool")
        if tool_name and tool_name in self.VALID_TOOL_NAMES:
            # Unified key name name / parameters
            if "tool" in data:
                data["name"] = data.pop("tool")
            if "params" in data and "parameters" not in data:
                data["parameters"] = data.pop("params")
            return True
        return False
    
    def _get_tools_description(self, tool_names: Optional[List[str]] = None) -> str:
        """Generate tool description text"""
        desc_parts = ["Available tools:"]
        selected_names = tool_names or list(self.tools.keys())
        for name in selected_names:
            tool = self.tools[name]
            params_desc = ", ".join([f"{k}: {v}" for k, v in tool["parameters"].items()])
            desc_parts.append(f"- {name}: {tool['description']}")
            if params_desc:
                desc_parts.append(f"  parameter:{params_desc}")
        return "\n".join(desc_parts)
    
    def plan_outline(
        self, 
        progress_callback: Optional[Callable] = None
    ) -> ReportOutline:
        """
        Planning report outline
        
        Use LLM to analyze simulation requirements and plan the directory structure of the report
        
        Args:
            progress_callback: progress callback function
            
        Returns:
            ReportOutline: report outline
        """
        logger.info("Start planning your report outline...")

        if self.fast_report_mode:
            if progress_callback:
                progress_callback("planning", 20, "Building OPS report outline...")
            outline = self._build_ops_fast_outline()
            if progress_callback:
                progress_callback("planning", 100, "OPS report outline prepared")
            logger.info(f"OPS fast outline prepared:{len(outline.sections)} chapters")
            return outline
        
        if progress_callback:
            progress_callback("planning", 0, "Analyzing simulation requirements...")
        
        # First get the simulation context
        context = self.zep_tools.get_simulation_context(
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement
        )
        
        if progress_callback:
            progress_callback("planning", 30, "Generating report outline...")
        
        system_prompt = PLAN_SYSTEM_PROMPT
        user_prompt = PLAN_USER_PROMPT_TEMPLATE.format(
            simulation_requirement=self.simulation_requirement,
            total_nodes=context.get('graph_statistics', {}).get('total_nodes', 0),
            total_edges=context.get('graph_statistics', {}).get('total_edges', 0),
            entity_types=list(context.get('graph_statistics', {}).get('entity_types', {}).keys()),
            total_entities=context.get('total_entities', 0),
            related_facts_json=json.dumps(context.get('related_facts', [])[:10], ensure_ascii=False, indent=2),
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            if progress_callback:
                progress_callback("planning", 80, "Parsing outline structure...")
            
            # Analyze the outline
            sections = []
            for section_data in response.get("sections", []):
                sections.append(ReportSection(
                    title=section_data.get("title", ""),
                    content=""
                ))
            
            outline = ReportOutline(
                title=response.get("title", "Simulation analysis report"),
                summary=response.get("summary", ""),
                sections=sections
            )
            
            if progress_callback:
                progress_callback("planning", 100, "Outline planning completed")
            
            logger.info(f"Outline planning completed:{len(sections)} chapters")
            return outline
            
        except Exception as e:
            logger.error(f"Outline planning failed:{str(e)}")
            # Return to default outline (3 chapters, as fallback)
            return ReportOutline(
                title="Future Forecast Report",
                summary="Future trend and risk analysis based on simulation forecasts",
                sections=[
                    ReportSection(title="Predictive scenarios and core findings"),
                    ReportSection(title="Predictive analysis of crowd behavior"),
                    ReportSection(title="Trend Outlook and Risk Warning")
                ]
            )
    
    def _generate_section_react(
        self, 
        section: ReportSection,
        outline: ReportOutline,
        previous_sections: List[str],
        progress_callback: Optional[Callable] = None,
        section_index: int = 0
    ) -> str:
        """
        Generate single chapter content using ReACT mode
        
        ReACT loop:
        1. Thought - what information is needed for analysis
        2. Action - call the tool to obtain information
        3. Observation â€“ Analysis tools return results
        4. Repeat until the information is enough or the maximum number of times is reached
        5. Final Answer - Generate chapter content
        
        Args:
            section: the section to generate
            outline: complete outline
            previous_sections: content of previous sections (used to maintain coherence)
            progress_callback: progress callback
            section_index: Section index (for logging)
            
        Returns:
            Chapter content (Markdown format)
        """
        logger.info(f"ReACT generates chapters:{section.title}")
        
        # Record chapter start log
        if self.report_logger:
            self.report_logger.log_section_start(section.title, section_index)
        
        max_iterations = 3 if self.fast_report_mode else 5
        min_tool_calls = 1 if self.fast_report_mode else 3
        max_tool_calls = 2 if self.fast_report_mode else self.MAX_TOOL_CALLS_PER_SECTION
        max_tokens = 1536 if self.fast_report_mode else 4096
        temperature = 0.35 if self.fast_report_mode else 0.5
        allowed_tools = self._get_fast_section_tool_names(section_index) if self.fast_report_mode else list(self.tools.keys())

        system_prompt = SECTION_SYSTEM_PROMPT_TEMPLATE.format(
            report_title=outline.title,
            report_summary=outline.summary,
            simulation_requirement=self.simulation_requirement,
            section_title=section.title,
            tools_description=self._get_tools_description(tool_names=allowed_tools),
        )
        system_prompt = system_prompt.replace(
            "Call tools at least 3 times per chapter and at most 5 times",
            f"Call tools at least {min_tool_calls} times per chapter and at most {max_tool_calls} times",
        ).replace(
            "[Available Search Tools] (call tools 3-5 times per chapter)",
            f"[Available Search Tools] (call tools {min_tool_calls}-{max_tool_calls} times per chapter)",
        )
        if self.fast_report_mode:
            system_prompt += (
                "\n\n[OPS fast report mode]\n"
                "- Keep the chapter concise and operational.\n"
                "- Prefer direct findings over long exposition.\n"
                "- Target roughly 4-6 short paragraphs or equivalent bullets.\n"
                "- Use only the listed lightweight tools for this chapter.\n"
            )

        # Build user prompt - pass in a maximum of 4000 words for each completed chapter
        if previous_sections:
            previous_parts = []
            source_sections = previous_sections[-1:] if self.fast_report_mode else previous_sections
            max_previous_chars = 2000 if self.fast_report_mode else 4000
            for sec in source_sections:
                truncated = sec[:max_previous_chars] + "..." if len(sec) > max_previous_chars else sec
                previous_parts.append(truncated)
            previous_content = "\n\n---\n\n".join(previous_parts)
        else:
            previous_content = "(This is the first chapter)"
        
        user_prompt = SECTION_USER_PROMPT_TEMPLATE.format(
            previous_content=previous_content,
            section_title=section.title,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # ReACT loop
        tool_calls_count = 0
        used_tools = set()  # Record the tool name that has been called
        all_tools = set(allowed_tools)
        best_final_answer = ""
        last_non_empty_response = ""
        consecutive_final_only_responses = 0

        # Report context for sub-issue generation in InsightForge
        report_context = f"Chapter title:{section.title}\nSimulation requirements:{self.simulation_requirement}"
        
        for iteration in range(max_iterations):
            if progress_callback:
                progress_callback(
                    "generating", 
                    int((iteration / max_iterations) * 100),
                    f"In-depth search and writing in progress ({tool_calls_count}/{max_tool_calls})"
                )
            
            # Call LLM
            response = self.llm.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Check if LLM return is None (API exception or empty content)
            if response is None:
                logger.warning(f"chapter{section.title} No.{iteration + 1} iterations: LLM returns None")
                # If there are still more iterations left, add a message and try again
                if iteration < max_iterations - 1:
                    messages.append({"role": "assistant", "content": "(response is empty)"})
                    messages.append({"role": "user", "content": "Please keep generating content."})
                    continue
                # The last iteration also returns None, jumping out of the loop and entering forced closing.
                break

            logger.debug(f"LLM response:{response[:200]}...")
            if response.strip():
                last_non_empty_response = response.strip()

            # Parse once and reuse the results
            tool_calls = self._parse_tool_calls(response)
            has_tool_calls = bool(tool_calls)
            has_final_answer = "Final Answer:" in response

            final_answer_candidate = self._extract_final_answer(response) if has_final_answer else ""
            if final_answer_candidate:
                best_final_answer = final_answer_candidate
            if has_final_answer and not has_tool_calls:
                consecutive_final_only_responses += 1
            else:
                consecutive_final_only_responses = 0

            # â”€â”€ Deterministic conflict handling: mixed tool call + Final Answer â”€â”€
            if has_tool_calls and has_final_answer:
                logger.warning(
                    f"chapter{section.title} No.{iteration+1} wheel:"
                    " LLM outputs tool calls and Final Answer simultaneously; "
                    "resolving deterministically"
                )
                if tool_calls_count < min_tool_calls:
                    logger.info(
                        f"chapter{section.title}: tool quota not met ({tool_calls_count}/{min_tool_calls}), "
                        "preferring the first valid tool call"
                    )
                    has_final_answer = False
                elif final_answer_candidate:
                    logger.info(
                        f"chapter{section.title}: tool quota satisfied ({tool_calls_count}/{min_tool_calls}), "
                        "accepting Final Answer and ignoring tool calls"
                    )
                    has_tool_calls = False
                    tool_calls = []
                else:
                    logger.warning(
                        f"chapter{section.title}: mixed response has no usable Final Answer content; "
                        "executing the first valid tool call"
                    )
                    has_final_answer = False

            # Logging LLM responses
            if self.report_logger:
                self.report_logger.log_llm_response(
                    section_title=section.title,
                    section_index=section_index,
                    response=response,
                    iteration=iteration + 1,
                    has_tool_calls=has_tool_calls,
                    has_final_answer=has_final_answer
                )

            # â”€â”€ Case 1: LLM outputs Final Answer â”€â”€
            if has_final_answer:
                # The number of times the tool has been called is insufficient. Refuse and ask to continue adjusting the tool.
                if tool_calls_count < min_tool_calls:
                    if tool_calls_count > 0 and best_final_answer and consecutive_final_only_responses >= 2:
                        logger.warning(
                            f"chapter{section.title} Unable to reach the ideal tool quota after repeated "
                            "final-answer-only responses; accepting the best available content to avoid stalling"
                        )
                        if self.report_logger:
                            self.report_logger.log_section_content(
                                section_title=section.title,
                                section_index=section_index,
                                content=best_final_answer,
                                tool_calls_count=tool_calls_count
                            )
                        return best_final_answer

                    messages.append({"role": "assistant", "content": response})
                    unused_tools = all_tools - used_tools
                    unused_hint = f"(These tools have not been used yet, it is recommended to use them:{', '.join(unused_tools)}ï¼‰" if unused_tools else ""
                    messages.append({
                        "role": "user",
                        "content": REACT_INSUFFICIENT_TOOLS_MSG.format(
                            tool_calls_count=tool_calls_count,
                            min_tool_calls=min_tool_calls,
                            unused_hint=unused_hint,
                        ),
                    })
                    continue

                # End normally
                final_answer = final_answer_candidate
                logger.info(f"chapter{section.title} Generation completed (tool call:{tool_calls_count}Second-rate)")

                if self.report_logger:
                    self.report_logger.log_section_content(
                        section_title=section.title,
                        section_index=section_index,
                        content=final_answer,
                        tool_calls_count=tool_calls_count
                    )
                return final_answer

            # â”€â”€ Case 2: LLM attempts to call the tool â”€â”€
            if has_tool_calls:
                # The tool quota has been exhausted â†’ clearly inform and require output Final Answer
                if tool_calls_count >= max_tool_calls:
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": REACT_TOOL_LIMIT_MSG.format(
                            tool_calls_count=tool_calls_count,
                            max_tool_calls=max_tool_calls,
                        ),
                    })
                    continue

                # Only execute the first tool call
                call = tool_calls[0]
                if call["name"] not in allowed_tools:
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Use only these tools for this chapter: {', '.join(allowed_tools)}. "
                            "Choose one of them and continue."
                        ),
                    })
                    continue
                if len(tool_calls) > 1:
                    logger.info(f"LLM attempts to call{len(tool_calls)} tools, only the first one is executed:{call['name']}")

                if self.report_logger:
                    self.report_logger.log_tool_call(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        parameters=call.get("parameters", {}),
                        iteration=iteration + 1
                    )

                result = self._execute_tool(
                    call["name"],
                    call.get("parameters", {}),
                    report_context=report_context
                )

                if self.report_logger:
                    self.report_logger.log_tool_result(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        result=result,
                        iteration=iteration + 1
                    )

                tool_calls_count += 1
                used_tools.add(call['name'])

                # Build unused tooltip
                unused_tools = all_tools - used_tools
                unused_hint = ""
                if unused_tools and tool_calls_count < max_tool_calls:
                    unused_hint = REACT_UNUSED_TOOLS_HINT.format(unused_list="ã€".join(unused_tools))

                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": REACT_OBSERVATION_TEMPLATE.format(
                        tool_name=call["name"],
                        result=result,
                        tool_calls_count=tool_calls_count,
                        max_tool_calls=max_tool_calls,
                        used_tools_str=", ".join(used_tools),
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # â”€â”€ Case 3: There is neither tool call nor Final Answer â”€â”€
            messages.append({"role": "assistant", "content": response})

            if tool_calls_count < min_tool_calls:
                # The number of times the tool has been called is insufficient. Unused tools are recommended.
                unused_tools = all_tools - used_tools
                unused_hint = f"(These tools have not been used yet, it is recommended to use them:{', '.join(unused_tools)}ï¼‰" if unused_tools else ""

                messages.append({
                    "role": "user",
                    "content": REACT_INSUFFICIENT_TOOLS_MSG_ALT.format(
                        tool_calls_count=tool_calls_count,
                        min_tool_calls=min_tool_calls,
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # The tool call is sufficient, LLM outputs the content without the "Final Answer:" prefix
            # Use this content directly as the final answer, no more idling
            logger.info(f"chapter{section.title} The 'Final Answer:' prefix is â€‹â€‹not detected, and the LLM output is directly adopted as the final content (tool call:{tool_calls_count}Second-rate)")
            final_answer = response.strip()

            if self.report_logger:
                self.report_logger.log_section_content(
                    section_title=section.title,
                    section_index=section_index,
                    content=final_answer,
                    tool_calls_count=tool_calls_count
                )
            return final_answer
        
        # The maximum number of iterations is reached and content is forced to be generated.
        logger.warning(f"chapter{section.title} The maximum number of iterations is reached and forced generation")
        if best_final_answer:
            logger.warning(
                f"chapter{section.title} Reuse the best available Final Answer after max iterations "
                f"(tool call:{tool_calls_count}Second-rate)"
            )
            final_answer = best_final_answer
        elif last_non_empty_response:
            logger.warning(
                f"chapter{section.title} No explicit Final Answer available after max iterations; "
                "using the last non-empty response as fallback"
            )
            final_answer = self._extract_final_answer(last_non_empty_response)
        else:
            messages.append({"role": "user", "content": REACT_FORCE_FINAL_MSG})
            
            response = self.llm.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Check if LLM returns None when forced closing
            if response is None:
                logger.error(f"chapter{section.title} When forcing closing, LLM returns None and uses the default error prompt.")
                final_answer = f"(Generation of this chapter failed: LLM returned an empty response, please try again later)"
            else:
                final_answer = self._extract_final_answer(response)

        # Record chapter content and generate completion log
        if self.report_logger:
            self.report_logger.log_section_content(
                section_title=section.title,
                section_index=section_index,
                content=final_answer,
                tool_calls_count=tool_calls_count
            )
        
        return final_answer
    
    def generate_report(
        self, 
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
        report_id: Optional[str] = None
    ) -> Report:
        """
        Generate a complete report (real-time output in chapters)
        
        Each chapter is saved to a folder immediately after being generated, without waiting for the entire report to be completed.
        File structure:
        reports/{report_id}/
            meta.json - reports meta information
            outline.json - Report outline
            progress.json - Generate progress
            section_01.md - Chapter 1
            section_02.md â€“ Chapter 2
            ...
            full_report.md â€“ full report
        
        Args:
            progress_callback: progress callback function (stage, progress, message)
            report_id: report ID (optional, automatically generated if not passed)
            
        Returns:
            Report: full report
        """
        import uuid
        
        # If report_id is not passed in, it will be automatically generated
        if not report_id:
            report_id = f"report_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now()
        
        report = Report(
            report_id=report_id,
            simulation_id=self.simulation_id,
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement,
            status=ReportStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # List of completed chapter titles (for progress tracking)
        completed_section_titles = []
        
        try:
            # Initialization: Create report folder and save initial state
            ReportManager._ensure_report_folder(report_id)
            
            # Initialize the logger (structured log agent_log.jsonl)
            self.report_logger = ReportLogger(report_id)
            self.report_logger.log_start(
                simulation_id=self.simulation_id,
                graph_id=self.graph_id,
                simulation_requirement=self.simulation_requirement
            )
            
            # Initialize the console logger (console_log.txt)
            self.console_logger = ReportConsoleLogger(report_id)
            
            ReportManager.update_progress(
                report_id, "pending", 0, "Initialization report...",
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            # Phase 1: Planning Outline
            report.status = ReportStatus.PLANNING
            ReportManager.update_progress(
                report_id, "planning", 5, "Start planning your report outline...",
                completed_sections=[]
            )
            
            # Record planning start log
            self.report_logger.log_planning_start()
            
            if progress_callback:
                progress_callback("planning", 0, "Start planning your report outline...")
            
            outline = self.plan_outline(
                progress_callback=lambda stage, prog, msg: 
                    progress_callback(stage, prog // 5, msg) if progress_callback else None
            )
            report.outline = outline
            
            # Record planning completion log
            self.report_logger.log_planning_complete(outline.to_dict())
            
            # Save outline to file
            ReportManager.save_outline(report_id, outline)
            ReportManager.update_progress(
                report_id, "planning", 15, f"Outline planning is completed, a total of{len(outline.sections)}chapters",
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            logger.info(f"Outline saved to file:{report_id}/outline.json")
            
            # Stage 2: Generate chapter by chapter (save in chapters)
            report.status = ReportStatus.GENERATING
            
            total_sections = len(outline.sections)
            generated_sections = []  # Save content for context
            
            for i, section in enumerate(outline.sections):
                section_num = i + 1
                base_progress = 20 + int((i / total_sections) * 70)
                
                # update progress
                ReportManager.update_progress(
                    report_id, "generating", base_progress,
                    f"Generating chapters:{section.title} ({section_num}/{total_sections})",
                    current_section=section.title,
                    completed_sections=completed_section_titles
                )
                
                if progress_callback:
                    progress_callback(
                        "generating", 
                        base_progress, 
                        f"Generating chapters:{section.title} ({section_num}/{total_sections})"
                    )
                
                # Generate main chapter content
                section_content = self._generate_section_react(
                    section=section,
                    outline=outline,
                    previous_sections=generated_sections,
                    progress_callback=lambda stage, prog, msg:
                        progress_callback(
                            stage, 
                            base_progress + int(prog * 0.7 / total_sections),
                            msg
                        ) if progress_callback else None,
                    section_index=section_num
                )
                
                section.content = section_content
                generated_sections.append(f"## {section.title}\n\n{section_content}")

                # save chapter
                ReportManager.save_section(report_id, section_num, section)
                completed_section_titles.append(section.title)

                # Record chapter completion log
                full_section_content = f"## {section.title}\n\n{section_content}"

                if self.report_logger:
                    self.report_logger.log_section_full_complete(
                        section_title=section.title,
                        section_index=section_num,
                        full_content=full_section_content.strip()
                    )

                logger.info(f"Chapter saved:{report_id}/section_{section_num:02d}.md")
                
                # update progress
                ReportManager.update_progress(
                    report_id, "generating", 
                    base_progress + int(70 / total_sections),
                    f"chapter{section.title} Completed",
                    current_section=None,
                    completed_sections=completed_section_titles
                )
            
            # Stage 3: Assembling the complete report
            if progress_callback:
                progress_callback("generating", 95, "Assembling full report...")
            
            ReportManager.update_progress(
                report_id, "generating", 95, "Assembling full report...",
                completed_sections=completed_section_titles
            )
            
            # Assemble a complete report using ReportManager
            report.markdown_content = ReportManager.assemble_full_report(report_id, outline)
            report.status = ReportStatus.COMPLETED
            report.completed_at = datetime.now().isoformat()
            
            # Calculate total time
            total_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Record report completion log
            if self.report_logger:
                self.report_logger.log_report_complete(
                    total_sections=total_sections,
                    total_time_seconds=total_time_seconds
                )
            
            # Save final report
            ReportManager.save_report(report)
            ReportManager.update_progress(
                report_id, "completed", 100, "Report generation completed",
                completed_sections=completed_section_titles
            )
            
            if progress_callback:
                progress_callback("completed", 100, "Report generation completed")
            
            logger.info(f"Report generation completed:{report_id}")
            
            # Turn off the console logger
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed:{str(e)}")
            report.status = ReportStatus.FAILED
            report.error = str(e)
            
            # Record error log
            if self.report_logger:
                self.report_logger.log_error(str(e), "failed")
            
            # Save failed status
            try:
                ReportManager.save_report(report)
                ReportManager.update_progress(
                    report_id, "failed", -1, f"Report generation failed:{str(e)}",
                    completed_sections=completed_section_titles
                )
            except Exception:
                pass  # Ignore save failed errors
            
            # Turn off the console logger
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
    
    def chat(
        self, 
        message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Talk to Report Agent
        
        During the conversation, the Agent can independently call the retrieval tool to answer questions.
        
        Args:
            message: user message
            chat_history: conversation history
            
        Returns:
            {
                "response": "Agent reply",
                "tool_calls": [list of called tools],
                "sources": [information sources]
            }
        """
        logger.info(f"Report Agent dialogue:{message[:50]}...")
        
        chat_history = chat_history or []
        
        # Get generated report content
        report_content = ""
        try:
            report = ReportManager.get_report_by_simulation(self.simulation_id)
            if report and report.markdown_content:
                # Limit report length to avoid long context
                report_content = report.markdown_content[:15000]
                if len(report.markdown_content) > 15000:
                    report_content += "\\n\\n... [Report truncated] ..."
        except Exception as e:
            logger.warning(f"Failed to get report content:{e}")
        
        system_prompt = CHAT_SYSTEM_PROMPT_TEMPLATE.format(
            simulation_requirement=self.simulation_requirement,
            report_content=report_content if report_content else "(No report yet)",
            tools_description=self._get_tools_description(),
        )

        # Build message
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add historical conversation
        for h in chat_history[-10:]:  # Limit history length
            messages.append(h)
        
        # Add user message
        messages.append({
            "role": "user", 
            "content": message
        })
        
        # ReACT loop (simplified version)
        tool_calls_made = []
        max_iterations = 2  # Reduce the number of iteration rounds
        
        for iteration in range(max_iterations):
            response = self.llm.chat(
                messages=messages,
                temperature=0.5
            )
            
            # Parsing tool call
            tool_calls = self._parse_tool_calls(response)
            
            if not tool_calls:
                # There is no tool call and the response is returned directly
                clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
                
                return {
                    "response": clean_response.strip(),
                    "tool_calls": tool_calls_made,
                    "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
                }
            
            # Perform tool calls (limited number)
            tool_results = []
            for call in tool_calls[:1]:  # Execute at most 1 tool call per round
                if len(tool_calls_made) >= self.MAX_TOOL_CALLS_PER_CHAT:
                    break
                result = self._execute_tool(call["name"], call.get("parameters", {}))
                tool_results.append({
                    "tool": call["name"],
                    "result": result[:1500]  # Limit result length
                })
                tool_calls_made.append(call)
            
            # Add results to message
            messages.append({"role": "assistant", "content": response})
            observation = "\n".join([f"[{r['tool']}results]\n{r['result']}" for r in tool_results])
            messages.append({
                "role": "user",
                "content": observation + CHAT_OBSERVATION_SUFFIX
            })
        
        # Reach the maximum iteration and get the final response
        final_response = self.llm.chat(
            messages=messages,
            temperature=0.5
        )
        
        # Clean response
        clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', final_response, flags=re.DOTALL)
        clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
        
        return {
            "response": clean_response.strip(),
            "tool_calls": tool_calls_made,
            "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
        }


class ReportManager:
    """
    report manager
    
    Responsible for persistent storage and retrieval of reports
    
    File structure (output in chapters):
    reports/
      {report_id}/
        meta.json - reports meta information and status
        outline.json - Report outline
        progress.json - Generate progress
        section_01.md - Chapter 1
        section_02.md â€“ Chapter 2
        ...
        full_report.md â€“ full report
    """
    
    # Report storage directory
    REPORTS_DIR = os.path.join(Config.UPLOAD_FOLDER, 'reports')
    
    @classmethod
    def _ensure_reports_dir(cls):
        """Make sure the report root directory exists"""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
    
    @classmethod
    def _get_report_folder(cls, report_id: str) -> str:
        """Get report folder path"""
        return os.path.join(cls.REPORTS_DIR, report_id)
    
    @classmethod
    def _ensure_report_folder(cls, report_id: str) -> str:
        """Make sure the reports folder exists and return the path"""
        folder = cls._get_report_folder(report_id)
        os.makedirs(folder, exist_ok=True)
        return folder
    
    @classmethod
    def _get_report_path(cls, report_id: str) -> str:
        """Get report metainformation file path"""
        return os.path.join(cls._get_report_folder(report_id), "meta.json")
    
    @classmethod
    def _get_report_markdown_path(cls, report_id: str) -> str:
        """Get the full report Markdown file path"""
        return os.path.join(cls._get_report_folder(report_id), "full_report.md")
    
    @classmethod
    def _get_outline_path(cls, report_id: str) -> str:
        """Get outline file path"""
        return os.path.join(cls._get_report_folder(report_id), "outline.json")
    
    @classmethod
    def _get_progress_path(cls, report_id: str) -> str:
        """Get progress file path"""
        return os.path.join(cls._get_report_folder(report_id), "progress.json")
    
    @classmethod
    def _get_section_path(cls, report_id: str, section_index: int) -> str:
        """Get the chapter Markdown file path"""
        return os.path.join(cls._get_report_folder(report_id), f"section_{section_index:02d}.md")
    
    @classmethod
    def _get_agent_log_path(cls, report_id: str) -> str:
        """Get Agent log file path"""
        return os.path.join(cls._get_report_folder(report_id), "agent_log.jsonl")
    
    @classmethod
    def _get_console_log_path(cls, report_id: str) -> str:
        """Get console log file path"""
        return os.path.join(cls._get_report_folder(report_id), "console_log.txt")
    
    @classmethod
    def get_console_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        Get console log content
        
        This is the console output log (INFO, WARNING, etc.) during the report generation process,
        Different from the structured log of agent_log.jsonl.
        
        Args:
            report_id: report ID
            from_line: From which line to start reading (for incremental acquisition, 0 means starting from the beginning)
            
        Returns:
            {
                "logs": [list of log lines],
                "total_lines": total number of lines,
                "from_line": starting line number,
                "has_more": whether there are more logs
            }
        """
        log_path = cls._get_console_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    # Keep original log lines, remove trailing newlines
                    logs.append(line.rstrip('\n\r'))
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # Read to the end
        }
    
    @classmethod
    def get_console_log_stream(cls, report_id: str) -> List[str]:
        """
        Get the complete console log (get it all at once)
        
        Args:
            report_id: report ID
            
        Returns:
            List of log lines
        """
        result = cls.get_console_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def get_agent_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        Get Agent log content
        
        Args:
            report_id: report ID
            from_line: From which line to start reading (for incremental acquisition, 0 means starting from the beginning)
            
        Returns:
            {
                "logs": [list of log entries],
                "total_lines": total number of lines,
                "from_line": starting line number,
                "has_more": whether there are more logs
            }
        """
        log_path = cls._get_agent_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        # Skip lines that failed to parse
                        continue
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # Read to the end
        }
    
    @classmethod
    def get_agent_log_stream(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete Agent log (for getting all at once)
        
        Args:
            report_id: report ID
            
        Returns:
            List of log entries
        """
        result = cls.get_agent_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def save_outline(cls, report_id: str, outline: ReportOutline) -> None:
        """
        Save report outline
        
        Called immediately after the planning phase is complete
        """
        cls._ensure_report_folder(report_id)
        
        with open(cls._get_outline_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(outline.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Outline saved:{report_id}")
    
    @classmethod
    def save_section(
        cls,
        report_id: str,
        section_index: int,
        section: ReportSection
    ) -> str:
        """
        Save a single chapter

        Called immediately after each chapter is generated to achieve chapter-by-chapter output.

        Args:
            report_id: report ID
            section_index: section index (starting from 1)
            section: Chapter object

        Returns:
            Saved file path
        """
        cls._ensure_report_folder(report_id)

        # Build chapter Markdown content - clean up possible duplicate titles
        cleaned_content = cls._clean_section_content(section.content, section.title)
        md_content = f"## {section.title}\n\n"
        if cleaned_content:
            md_content += f"{cleaned_content}\n\n"

        # save file
        file_suffix = f"section_{section_index:02d}.md"
        file_path = os.path.join(cls._get_report_folder(report_id), file_suffix)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"Chapter saved:{report_id}/{file_suffix}")
        return file_path
    
    @classmethod
    def _clean_section_content(cls, content: str, section_title: str) -> str:
        """
        Clean up chapter content
        
        1. Remove the Markdown title line that duplicates the chapter title at the beginning of the content
        2. Convert all ### and below level headings to bold text
        
        Args:
            content: original content
            section_title: Section title
            
        Returns:
            Cleaned content
        """
        import re
        
        if not content:
            return content
        
        content = content.strip()
        lines = content.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check if it is a Markdown header row
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title_text = heading_match.group(2).strip()
                
                # Check if the title is a duplicate of the chapter title (skip duplicates within the first 5 lines)
                if i < 5:
                    if title_text == section_title or title_text.replace(' ', '') == section_title.replace(' ', ''):
                        skip_next_empty = True
                        continue
                
                # Convert all levels of headings (#, ##, ###, ####, etc.) to bold
                # Because chapter titles are added by the system, there should be no titles in the content
                cleaned_lines.append(f"**{title_text}**")
                cleaned_lines.append("")  # add blank line
                continue
            
            # If the previous line is a skipped title and the current line is empty, it is also skipped.
            if skip_next_empty and stripped == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        # Remove leading blank lines
        while cleaned_lines and cleaned_lines[0].strip() == '':
            cleaned_lines.pop(0)
        
        # Remove leading separator
        while cleaned_lines and cleaned_lines[0].strip() in ['---', '***', '___']:
            cleaned_lines.pop(0)
            # Also remove empty lines after separators
            while cleaned_lines and cleaned_lines[0].strip() == '':
                cleaned_lines.pop(0)
        
        return '\n'.join(cleaned_lines)
    
    @classmethod
    def update_progress(
        cls, 
        report_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_section: str = None,
        completed_sections: List[str] = None
    ) -> None:
        """
        Update report generation progress
        
        The front end can obtain real-time progress by reading progress.json
        """
        cls._ensure_report_folder(report_id)
        
        progress_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "current_section": current_section,
            "completed_sections": completed_sections or [],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(cls._get_progress_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_progress(cls, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report generation progress"""
        path = cls._get_progress_path(report_id)
        
        if not os.path.exists(path):
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def get_generated_sections(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        Get the generated chapter list
        
        Returns all saved chapter file information
        """
        folder = cls._get_report_folder(report_id)
        
        if not os.path.exists(folder):
            return []
        
        sections = []
        for filename in sorted(os.listdir(folder)):
            if filename.startswith('section_') and filename.endswith('.md'):
                file_path = os.path.join(folder, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse chapter index from filename
                parts = filename.replace('.md', '').split('_')
                section_index = int(parts[1])

                sections.append({
                    "filename": filename,
                    "section_index": section_index,
                    "content": content
                })

        return sections
    
    @classmethod
    def assemble_full_report(cls, report_id: str, outline: ReportOutline) -> str:
        """
        Assemble the complete report
        
        Assemble full report from saved chapter files with title cleaning
        """
        folder = cls._get_report_folder(report_id)
        
        # Build report header
        md_content = f"# {outline.title}\n\n"
        md_content += f"> {outline.summary}\n\n"
        md_content += f"---\n\n"
        
        # Read all chapter files sequentially
        sections = cls.get_generated_sections(report_id)
        for section_info in sections:
            md_content += section_info["content"]
        
        # Post-processing: Clean up title issues throughout the report
        md_content = cls._post_process_report(md_content, outline)
        
        # Save full report
        full_path = cls._get_report_markdown_path(report_id)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Full report assembled:{report_id}")
        return md_content
    
    @classmethod
    def _post_process_report(cls, content: str, outline: ReportOutline) -> str:
        """
        Post-processing report content
        
        1. Remove duplicate titles
        2. Keep the main title (#) and chapter title (##) of the report, and remove other levels of titles (###, ####, etc.)
        3. Clean up excess blank lines and separators
        
        Args:
            content: original report content
            outline: report outline
            
        Returns:
            Processed content
        """
        import re
        
        lines = content.split('\n')
        processed_lines = []
        prev_was_heading = False
        
        # Collect all chapter titles in the outline
        section_titles = set()
        for section in outline.sections:
            section_titles.add(section.title)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check if it is a header row
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # Check whether it is a duplicate title (titles with the same content appear within 5 consecutive lines)
                is_duplicate = False
                for j in range(max(0, len(processed_lines) - 5), len(processed_lines)):
                    prev_line = processed_lines[j].strip()
                    prev_match = re.match(r'^(#{1,6})\s+(.+)$', prev_line)
                    if prev_match:
                        prev_title = prev_match.group(2).strip()
                        if prev_title == title:
                            is_duplicate = True
                            break
                
                if is_duplicate:
                    # Skip repeated headers and empty lines after them
                    i += 1
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    continue
                
                # Title level processing:
                # - # (level=1) Only keep the main report title
                # - ## (level=2) keep chapter titles
                # - ### and below (level>=3) are converted to bold text
                
                if level == 1:
                    if title == outline.title:
                        # Keep report main title
                        processed_lines.append(line)
                        prev_was_heading = True
                    elif title in section_titles:
                        # Chapter title incorrectly uses #, corrected to ##
                        processed_lines.append(f"## {title}")
                        prev_was_heading = True
                    else:
                        # Other first-level headings are made bold
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                elif level == 2:
                    if title in section_titles or title == outline.title:
                        # Keep chapter titles
                        processed_lines.append(line)
                        prev_was_heading = True
                    else:
                        # Second-level headings that are not chapters are made bold
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                else:
                    # Titles at level ### and below are converted to bold text
                    processed_lines.append(f"**{title}**")
                    processed_lines.append("")
                    prev_was_heading = False
                
                i += 1
                continue
            
            elif stripped == '---' and prev_was_heading:
                # Skip the separator immediately following the title
                i += 1
                continue
            
            elif stripped == '' and prev_was_heading:
                # Leave only a blank line after the title
                if processed_lines and processed_lines[-1].strip() != '':
                    processed_lines.append(line)
                prev_was_heading = False
            
            else:
                processed_lines.append(line)
                prev_was_heading = False
            
            i += 1
        
        # Clean multiple consecutive empty lines (keep up to 2)
        result_lines = []
        empty_count = 0
        for line in processed_lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    @classmethod
    def save_report(cls, report: Report) -> None:
        """Save report meta information and full report"""
        cls._ensure_report_folder(report.report_id)
        
        # Save meta information JSON
        with open(cls._get_report_path(report.report_id), 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        # save outline
        if report.outline:
            cls.save_outline(report.report_id, report.outline)
        
        # Save complete Markdown report
        if report.markdown_content:
            with open(cls._get_report_markdown_path(report.report_id), 'w', encoding='utf-8') as f:
                f.write(report.markdown_content)
        
        logger.info(f"Report saved:{report.report_id}")
    
    @classmethod
    def get_report(cls, report_id: str) -> Optional[Report]:
        """Get report"""
        path = cls._get_report_path(report_id)
        
        if not os.path.exists(path):
            # Compatible with older formats: Check files stored directly in the reports directory
            old_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
            if os.path.exists(old_path):
                path = old_path
            else:
                return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Rebuild Report object
        outline = None
        if data.get('outline'):
            outline_data = data['outline']
            sections = []
            for s in outline_data.get('sections', []):
                sections.append(ReportSection(
                    title=s['title'],
                    content=s.get('content', '')
                ))
            outline = ReportOutline(
                title=outline_data['title'],
                summary=outline_data['summary'],
                sections=sections
            )
        
        # If markdown_content is empty, try reading from full_report.md
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            full_report_path = cls._get_report_markdown_path(report_id)
            if os.path.exists(full_report_path):
                with open(full_report_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
        
        return Report(
            report_id=data['report_id'],
            simulation_id=data['simulation_id'],
            graph_id=data['graph_id'],
            simulation_requirement=data['simulation_requirement'],
            status=ReportStatus(data['status']),
            outline=outline,
            markdown_content=markdown_content,
            created_at=data.get('created_at', ''),
            completed_at=data.get('completed_at', ''),
            error=data.get('error')
        )
    
    @classmethod
    def get_report_by_simulation(cls, simulation_id: str) -> Optional[Report]:
        """Get reports based on impersonation ID"""
        cls._ensure_reports_dir()
        
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # New format: folder
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report and report.simulation_id == simulation_id:
                    return report
            # Compatible with old formats: JSON files
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report and report.simulation_id == simulation_id:
                    return report
        
        return None
    
    @classmethod
    def list_reports(cls, simulation_id: Optional[str] = None, limit: int = 50) -> List[Report]:
        """list reports"""
        cls._ensure_reports_dir()
        
        reports = []
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # New format: folder
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
            # Compatible with old formats: JSON files
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
        
        # In descending order of creation time
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports[:limit]
    
    @classmethod
    def delete_report(cls, report_id: str) -> bool:
        """Delete report (entire folder)"""
        import shutil
        
        folder_path = cls._get_report_folder(report_id)
        
        # New format: delete entire folder
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            logger.info(f"Report folder deleted:{report_id}")
            return True
        
        # Compatible with older formats: delete individual files
        deleted = False
        old_json_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
        old_md_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.md")
        
        if os.path.exists(old_json_path):
            os.remove(old_json_path)
            deleted = True
        if os.path.exists(old_md_path):
            os.remove(old_md_path)
            deleted = True
        
        return deleted

