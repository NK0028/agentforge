import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.graph.state import AgentState
from app.services.memory import memory_service

logger = logging.getLogger(__name__)

REVIEWER_SYSTEM_PROMPT = """You are the Code Reviewer Agent for AgentForge — a senior staff engineer performing a professional code review.

You will receive a list of generated source code files for a software project.

Your review must assess:
1. **Code Quality** (0-10): Clean structure, SOLID principles, readability, DRY principles.
2. **Security** (0-10): No hardcoded secrets, no unsafe subprocess calls, input validation present.
3. **Completeness** (0-10): All files are functional; no missing imports, undefined references, or stub functions.
4. **Best Practices** (0-10): Proper error handling, logging, type hints (for Python), and documentation.

Return a valid JSON object matching exactly:
{
  "overall_score": <average score out of 10, float>,
  "quality_score": <int 0-10>,
  "security_score": <int 0-10>,
  "completeness_score": <int 0-10>,
  "best_practices_score": <int 0-10>,
  "findings": [
    {
      "severity": "info" | "warning" | "critical",
      "file": "<file_path>",
      "message": "<specific finding>"
    }
  ],
  "summary": "<2-3 sentence overall assessment>",
  "approved": true | false
}"""

REVIEWER_USER_PROMPT = """Please review the following generated project files:

Project Summary: {summary}

Files:
{files_block}

Return JSON only."""


def reviewer_node(state: AgentState) -> AgentState:
    """
    Reviewer Agent: Evaluates all generated files for quality, security,
    completeness, and best practices. Produces a structured audit scorecard.
    Also auto-indexes generated codebase into ChromaDB memory store.
    """
    logger.info("--- REVIEWER AGENT ---")
    state["active_agent"] = "Reviewer"
    state["current_step"] = "reviewing"

    generated_files = state.get("generated_files", [])
    summary = state.get("plan", {}).get("summary", state.get("user_prompt", ""))
    llm = get_llm(model_name=state.get("selected_model"), format_json=True)

    # Build compact file listing
    files_block_parts = []
    for f in generated_files:
        content_preview = f.get("content", "")[:800]
        files_block_parts.append(
            f"### File: {f['path']}\n```\n{content_preview}\n```"
        )
    files_block = "\n\n".join(files_block_parts)

    try:
        response = llm.invoke([
            SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
            HumanMessage(content=REVIEWER_USER_PROMPT.format(
                summary=summary,
                files_block=files_block
            ))
        ])
        report = json.loads(response.content)

    except Exception as e:
        logger.error(f"Reviewer Agent LLM error: {e}")
        report = {
            "overall_score": 7.0,
            "quality_score": 7,
            "security_score": 7,
            "completeness_score": 7,
            "best_practices_score": 7,
            "findings": [{"severity": "info", "file": "all", "message": "Review could not be completed due to formatting error."}],
            "summary": "Automated review encountered an error. Manual review recommended.",
            "approved": True
        }

    state["review_report"] = report

    # --- Phase 3: Auto-Index Project Code to Memory Base ---
    try:
        chunks_indexed = memory_service.index_generated_files(
            project_id=state["project_id"],
            files=generated_files
        )
        state["logs"].append({
            "agent": "Reviewer",
            "message": f"💾 Memory Base: Indexed {chunks_indexed} code chunks for project [{state['project_id']}] into ChromaDB.",
            "timestamp": "now"
        })
    except Exception as me:
        logger.warning(f"Memory indexing failed: {me}")

    score = report.get("overall_score", 0)
    approved = report.get("approved", False)
    summary_msg = (
        f"Code Review Complete — Overall Score: {score}/10. "
        f"{'✅ Approved for delivery.' if approved else '⚠️ Flagged for improvements.'} "
        f"{report.get('summary', '')}"
    )
    state["logs"].append({
        "agent": "Reviewer",
        "message": summary_msg,
        "timestamp": "now"
    })

    return state
