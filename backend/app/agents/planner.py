import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """You are the Lead Planner Agent for AgentForge.
Your task is to analyze the user prompt and generate an engineering project execution plan.

User Prompt: {user_prompt}

Return a valid JSON object:
{{
  "project_name": "<short-kebab-case-name>",
  "summary": "<2-sentence project summary>",
  "tech_stack": {{
    "frontend": "<e.g., HTML/JS/CSS or React>",
    "backend": "<e.g., Python/FastAPI>",
    "database": "<e.g., SQLite>"
  }},
  "milestones": [
    {{
      "step": 1,
      "title": "<milestone title>",
      "description": "<key requirements>"
    }},
    {{
      "step": 2,
      "title": "<milestone title>",
      "description": "<key requirements>"
    }}
  ]
}}"""

def planner_node(state: AgentState) -> AgentState:
    logger.info("--- PLANNER AGENT ---")
    state["active_agent"] = "Planner"
    state["current_step"] = "planning"
    
    llm = get_llm(model_name=state.get("selected_model"), format_json=True)
    prompt_str = PLANNER_PROMPT.format(user_prompt=state["user_prompt"])
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a JSON-only technical project manager."),
            HumanMessage(content=prompt_str)
        ])
        
        plan_data = json.loads(response.content)
        state["plan"] = plan_data
        
        log_entry = {
            "agent": "Planner",
            "message": f"Generated Project Plan: '{plan_data.get('project_name')}' with {len(plan_data.get('milestones', []))} milestones.",
            "timestamp": "now"
        }
    except Exception as e:
        logger.error(f"Planner Agent error: {e}")
        # Fallback plan if model JSON generation failed
        plan_data = {
            "project_name": "generated-app",
            "summary": f"Application built for: {state['user_prompt']}",
            "tech_stack": {"frontend": "HTML/JS", "backend": "FastAPI", "database": "SQLite"},
            "milestones": [
                {"step": 1, "title": "Foundation", "description": "Create core HTML & server code."}
            ]
        }
        state["plan"] = plan_data
        log_entry = {
            "agent": "Planner",
            "message": f"Generated fallback project plan due to format issue: {e}",
            "timestamp": "now"
        }
        
    state["logs"].append(log_entry)
    return state
