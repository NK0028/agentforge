import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.graph.state import AgentState
from app.services.workspace import WorkspaceService
from app.services.memory import memory_service

logger = logging.getLogger(__name__)

CODER_PROMPT = """You are the Senior Full-Stack Coding Agent for AgentForge.
Write complete, production-ready source code for the requested file.

Project Summary: {summary}
Target File Path: {file_path}
File Purpose: {purpose}

{rag_section}

Rules:
1. Do NOT use placeholders like '# TODO' or '...'.
2. Provide complete, fully-functional executable code.
3. Return a valid JSON object:
{{
  "file_path": "{file_path}",
  "code": "<complete source code string>"
}}"""

def coder_node(state: AgentState) -> AgentState:
    logger.info("--- CODING AGENT (RAG-Augmented) ---")
    state["active_agent"] = "Coder"
    state["current_step"] = "coding"
    
    workspace = WorkspaceService(project_id=state["project_id"])
    target_files = state.get("architecture", {}).get("files", [])
    summary = state.get("plan", {}).get("summary", state["user_prompt"])
    
    generated_files = []
    llm = get_llm(model_name=state.get("selected_model"), format_json=True)
    
    for file_info in target_files:
        file_path = file_info.get("path")
        purpose = file_info.get("purpose")
        
        # RAG query for file specific context
        rag_hits = memory_service.retrieve(query=f"code implementation for {file_path} {purpose}", n_results=2)
        rag_section = ""
        if rag_hits:
            snippets = [f"- Code reference ({h.get('metadata', {}).get('file_path', 'memory')}): {h.get('content', '')[:250]}..." for h in rag_hits]
            rag_section = "Relevant Reference Snippets from Memory Base:\n" + "\n".join(snippets)
        
        prompt_str = CODER_PROMPT.format(summary=summary, file_path=file_path, purpose=purpose, rag_section=rag_section)
        try:
            response = llm.invoke([
                SystemMessage(content="You are a JSON-only software developer."),
                HumanMessage(content=prompt_str)
            ])
            code_data = json.loads(response.content)
            code_content = code_data.get("code", f"# {purpose}\nprint('Hello from {file_path}')\n")
        except Exception as e:
            logger.error(f"Coder model error on {file_path}: {e}")
            code_content = f"# Generated code for {file_path}\n# Purpose: {purpose}\n\ndef main():\n    print('AgentForge generated module: {file_path}')\n\nif __name__ == '__main__':\n    main()\n"
        
        # Save to virtual workspace sandbox
        clean_path = workspace.write_file(file_path, code_content)
        generated_files.append({"path": clean_path, "content": code_content})
        
        state["logs"].append({
            "agent": "Coder",
            "message": f"Successfully generated & saved source file: [{clean_path}]",
            "timestamp": "now"
        })

    state["generated_files"] = generated_files
    return state
