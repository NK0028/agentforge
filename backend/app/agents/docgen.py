import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.graph.state import AgentState
from app.services.workspace import WorkspaceService

logger = logging.getLogger(__name__)

DOCGEN_SYSTEM_PROMPT = """You are the Documentation Agent for AgentForge.
Your job is to generate a comprehensive, professional open-source README.md file for the newly created user application.

Include:
- Project Title & High-Level Summary
- Features Breakdown
- Installation & Setup Instructions
- API Endpoints / Usage Examples
- File Structure Overview

Return a valid JSON object strictly matching:
{
  "readme_content": "<markdown content of README.md>"
}"""

def docgen_node(state: AgentState) -> AgentState:
    """
    Documentation Agent: Generates project README.md and usage guide
    and saves them directly into the output project workspace.
    """
    logger.info("--- DOCUMENTATION AGENT ---")
    state["active_agent"] = "DocGen"
    state["current_step"] = "documentation"

    workspace = WorkspaceService(project_id=state["project_id"])
    plan = state.get("plan", {})
    project_name = plan.get("project_name", "agentforge-app")
    summary = plan.get("summary", state["user_prompt"])
    tech_stack = plan.get("tech_stack", {})
    files = [f["path"] for f in state.get("generated_files", [])]

    user_prompt = f"""Generate a README.md for:
Project Name: {project_name}
Summary: {summary}
Tech Stack: {json.dumps(tech_stack)}
Files Created: {json.dumps(files)}
"""

    llm = get_llm(model_name=state.get("selected_model"), format_json=True)
    try:
        response = llm.invoke([
            SystemMessage(content=DOCGEN_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])
        doc_data = json.loads(response.content)
        readme_content = doc_data.get("readme_content", f"# {project_name}\n\n{summary}\n")
    except Exception as e:
        logger.error(f"DocGen LLM error: {e}")
        readme_content = f"# {project_name}\n\n> {summary}\n\n## Generated Files\n" + "\n".join([f"- `{f}`" for f in files])

    # Save to workspace sandbox
    saved_path = workspace.write_file("README.md", readme_content)
    
    docs_info = [{"path": saved_path, "content": readme_content}]
    state["docs_generated"] = docs_info
    
    # Append to generated_files list so it appears in CodeViewer UI
    state["generated_files"].append({"path": saved_path, "content": readme_content})

    state["logs"].append({
        "agent": "DocGen",
        "message": f"📝 Generated application README.md documentation file: [{saved_path}]",
        "timestamp": "now"
    })

    return state
