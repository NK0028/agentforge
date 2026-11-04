import json
import logging
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

def supervisor_node(state: AgentState) -> AgentState:
    logger.info("--- SUPERVISOR AGENT (Phase 4/5 HITL & DevOps) ---")
    state["active_agent"] = "Supervisor"

    # Deterministic routing logic across all 9 nodes
    if not state.get("plan"):
        next_node, reasoning = "planner", "No project plan found. Routing to Planner."
    elif not state.get("architecture"):
        next_node, reasoning = "architect", "Plan exists but no architecture spec. Routing to Architect."
    elif state.get("architecture") and not state.get("hitl_approved", False):
        # HITL Checkpoint: Pause pipeline and await human approval
        next_node, reasoning = "PAUSE_HITL", "Architecture spec ready. Awaiting Human-in-the-Loop approval."
        state["awaiting_approval"] = True
    elif not state.get("generated_files"):
        next_node, reasoning = "coder", "Architecture approved. Routing to Coder to generate code."
        state["awaiting_approval"] = False
    elif not state.get("test_results"):
        next_node, reasoning = "tester", "Files generated. Routing to Tester for syntax validation."
    elif not state.get("test_results", {}).get("overall_passed", False):
        next_node, reasoning = "debugger", "Tests failed. Routing to Debugger for root cause analysis & patching."
    elif not state.get("review_report"):
        next_node, reasoning = "reviewer", "All tests passed. Routing to Reviewer for code quality audit."
    elif not state.get("docs_generated"):
        next_node, reasoning = "docgen", "Code review complete. Routing to DocGen for application README creation."
    elif not state.get("deployment_files"):
        next_node, reasoning = "deployer", "Documentation created. Routing to Deployer for Docker & CI/CD generation."
    else:
        next_node, reasoning = "FINISH", "All phases complete. Project ready for delivery!"

    state["next_node"] = next_node
    if next_node == "PAUSE_HITL":
        state["current_step"] = "awaiting_approval"
    elif next_node == "FINISH":
        state["current_step"] = "completed"
    else:
        state["current_step"] = next_node

    state["logs"].append({
        "agent": "Supervisor",
        "message": f"Decision → [{next_node.upper()}] | {reasoning}",
        "timestamp": "now"
    })

    logger.info(f"Supervisor routing to: {next_node} — {reasoning}")
    return state
