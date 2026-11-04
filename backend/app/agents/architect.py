import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.graph.state import AgentState
from app.services.memory import memory_service

logger = logging.getLogger(__name__)

ARCHITECT_PROMPT = """You are the Principal Systems Architect Agent for AgentForge.
Analyze the project plan below and design the target file structure.

Project Plan:
{plan}

{rag_section}

Return a valid JSON object strictly matching:
{{
  "folder_structure": "<markdown file tree representation>",
  "files": [
    {{
      "path": "app.py",
      "purpose": "Main application entry point."
    }},
    {{
      "path": "index.html",
      "purpose": "User interface dashboard."
    }}
  ]
}}"""

def architect_node(state: AgentState) -> AgentState:
    logger.info("--- ARCHITECT AGENT (RAG-Augmented) ---")
    state["active_agent"] = "Architect"
    state["current_step"] = "architecture"
    
    prompt = state.get("user_prompt", "")
    plan_str = json.dumps(state.get("plan", {}), indent=2)
    
    # RAG Retrieval: Search memory base for relevant architecture patterns
    rag_hits = memory_service.retrieve(query=f"architecture design pattern {prompt}", n_results=3)
    state["rag_context"] = rag_hits
    
    rag_section = ""
    if rag_hits:
        snippets = [f"- Snippet ({h.get('metadata', {}).get('file_path', 'pattern')}): {h.get('content', '')[:200]}..." for h in rag_hits]
        rag_section = "Relevant Architectural Patterns & Prior Memory Hits:\n" + "\n".join(snippets)
        state["logs"].append({
            "agent": "Architect",
            "message": f"🧠 RAG Knowledge Base: Retrieved {len(rag_hits)} prior architecture patterns.",
            "timestamp": "now"
        })
    
    llm = get_llm(model_name=state.get("selected_model"), format_json=True)
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a JSON-only software architect."),
            HumanMessage(content=ARCHITECT_PROMPT.format(plan=plan_str, rag_section=rag_section))
        ])
        arch_data = json.loads(response.content)
        state["architecture"] = arch_data
        
        log_entry = {
            "agent": "Architect",
            "message": f"Designed software architecture with {len(arch_data.get('files', []))} target files.",
            "timestamp": "now"
        }
    except Exception as e:
        logger.error(f"Architect Agent error: {e}")
        arch_data = {
            "folder_structure": "- app.py\n- index.html",
            "files": [
                {"path": "main.py", "purpose": "Application server."},
                {"path": "index.html", "purpose": "Web UI."}
            ]
        }
        state["architecture"] = arch_data
        log_entry = {
            "agent": "Architect",
            "message": f"Generated fallback architecture spec due to format issue: {e}",
            "timestamp": "now"
        }

    state["logs"].append(log_entry)
    return state
