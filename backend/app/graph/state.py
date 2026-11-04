from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    project_id: str
    user_prompt: str
    selected_model: str
    current_step: str
    active_agent: str
    # Phase 1
    plan: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    generated_files: List[Dict[str, str]]
    # Phase 2
    test_results: Optional[Dict[str, Any]]          # stdout, stderr, exit_code, passed
    debug_reflections: List[Dict[str, Any]]          # traceback analysis & patch history
    review_report: Optional[Dict[str, Any]]          # quality score, security findings
    retry_count: int                                  # self-healing loop counter
    # Phase 3
    rag_context: List[Dict[str, Any]]               # retrieved memory snippets / context chunks
    # Phase 4 & 5
    hitl_approved: bool                             # human approval flag
    awaiting_approval: bool                         # pipeline paused state flag
    docs_generated: List[Dict[str, str]]             # README & guide docs
    deployment_files: List[Dict[str, str]]         # Dockerfile, docker-compose, CI/CD
    # Shared
    logs: List[Dict[str, Any]]
    next_node: str
    error: Optional[str]
