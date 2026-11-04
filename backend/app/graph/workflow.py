import logging
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.planner import planner_node
from app.agents.architect import architect_node
from app.agents.coder import coder_node
from app.agents.tester import tester_node
from app.agents.debugger import debugger_node
from app.agents.reviewer import reviewer_node
from app.agents.docgen import docgen_node
from app.agents.deployer import deployer_node

logger = logging.getLogger(__name__)

def route_next(state: AgentState) -> str:
    """Conditional router reading next_node from Supervisor decision."""
    next_node = state.get("next_node", "FINISH")
    if next_node in ["FINISH", "PAUSE_HITL"]:
        return END
    return next_node

def build_agent_graph():
    """
    Constructs the complete 9-Node AgentForge LangGraph pipeline.

    Pipeline:
        START → Supervisor → Planner → Architect → (HITL Approval) → Coder → Tester
                                                                                 ↓         ↓
                                                                             Debugger   Reviewer → DocGen → Deployer → END
    """
    workflow = StateGraph(AgentState)

    # --- Register all 9 agent nodes ---
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("debugger", debugger_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("docgen", docgen_node)
    workflow.add_node("deployer", deployer_node)

    # --- Entry point ---
    workflow.set_entry_point("supervisor")

    # --- Supervisor conditional routing ---
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "planner": "planner",
            "architect": "architect",
            "coder": "coder",
            "tester": "tester",
            "debugger": "debugger",
            "reviewer": "reviewer",
            "docgen": "docgen",
            "deployer": "deployer",
            END: END
        }
    )

    # --- Worker nodes return to Supervisor ---
    for node in ["planner", "architect", "coder", "tester", "debugger", "reviewer", "docgen", "deployer"]:
        workflow.add_edge(node, "supervisor")

    return workflow.compile()

agent_graph = build_agent_graph()
logger.info("AgentForge Phase 4/5 Complete 9-Node LangGraph compiled successfully.")
