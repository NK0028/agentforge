# AgentForge System Architecture 🏗️

AgentForge is built around an **event-driven, local-first, multi-agent orchestration architecture** powered by LangGraph, FastAPI, ChromaDB, and React.

---

## 🏛️ High-Level System Component Diagram

```mermaid
graph TB
    subgraph Frontend["🖥️ React Frontend (Vite + TypeScript + TailwindCSS)"]
        UI_Input["ProjectInput<br/>Prompt Bar"]
        UI_DAG["AgentDAG<br/>9-Node Pipeline Viz"]
        UI_Logs["LiveLogs<br/>SSE Stream Terminal"]
        UI_Code["CodeViewer<br/>File Browser + ZIP Export"]
        UI_Tests["TestResultsPanel<br/>Per-File Pass/Fail"]
        UI_Review["ReviewScoreCard<br/>4-Metric Audit"]
        UI_Memory["MemoryViewer<br/>ChromaDB Vector Search"]
        UI_HITL["HITLApprovalModal<br/>Architecture Review"]
    end

    subgraph Backend["⚙️ FastAPI Backend Engine"]
        API["REST API + SSE Stream"]
        HITL_Endpoint["POST /resume<br/>HITL Resume"]
        Export["GET /export<br/>ZIP Download"]
    end

    subgraph Graph["🧠 LangGraph State Machine (9 Nodes)"]
        SUP["👑 Supervisor"]
        PLAN["📋 Planner"]
        ARCH["📐 Architect"]
        CODE["💻 Coder"]
        TEST["🧪 Tester"]
        DEBUG["🐛 Debugger"]
        REV["📋 Reviewer"]
        DOC["📝 DocGen"]
        DEP["🐳 Deployer"]
    end

    subgraph Services["🔧 Backend Services"]
        WS["WorkspaceService<br/>Sandboxed File I/O"]
        MEM["MemoryService<br/>ChromaDB Vector Store"]
        LLM["LLM Factory<br/>ChatOllama Provider"]
    end

    subgraph External["🌐 External (Local)"]
        OLLAMA["Ollama Daemon<br/>qwen2.5-coder / deepseek-r1"]
        CHROMA["ChromaDB<br/>Persistent Vector DB"]
    end

    Frontend -->|"HTTP REST / SSE"| Backend
    Backend --> Graph
    Graph --> Services
    LLM --> OLLAMA
    MEM --> CHROMA
    SUP --> PLAN --> SUP
    SUP --> ARCH --> SUP
    SUP --> CODE --> SUP
    SUP --> TEST --> SUP
    SUP --> DEBUG --> SUP
    SUP --> REV --> SUP
    SUP --> DOC --> SUP
    SUP --> DEP --> SUP
```

---

## 🔄 Complete 9-Node LangGraph Execution Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🖥️ Frontend
    participant A as ⚙️ FastAPI
    participant S as 👑 Supervisor
    participant P as 📋 Planner
    participant AR as 📐 Architect
    participant H as 🛡️ HITL Gate
    participant C as 💻 Coder
    participant T as 🧪 Tester
    participant D as 🐛 Debugger
    participant R as 📋 Reviewer
    participant DG as 📝 DocGen
    participant DP as 🐳 Deployer

    U->>F: Enter software idea prompt
    F->>A: POST /api/agent/run
    A-->>F: SSE Stream begins
    A->>S: Initialize AgentState

    S->>P: Route → Planner (no plan)
    P-->>S: Returns project plan JSON
    S->>AR: Route → Architect (no architecture)
    AR-->>S: Returns file tree spec

    S->>H: Route → PAUSE_HITL
    A-->>F: event: awaiting_approval
    F->>U: Show Architecture Approval Modal
    U->>F: Approve / Edit file specs
    F->>A: POST /api/agent/resume/{id}
    A->>S: Resume with approved architecture

    S->>C: Route → Coder (approved, no files)
    C-->>S: Returns generated source code files

    S->>T: Route → Tester (files exist, no test_results)
    T-->>S: Returns per-file syntax check results

    alt Tests Failed
        S->>D: Route → Debugger
        D-->>S: Returns patched code files
        Note over S,T: Loop back to Tester (max 3 retries)
        S->>T: Re-test patched files
        T-->>S: Returns updated results
    end

    S->>R: Route → Reviewer (tests passed)
    R-->>S: Returns quality scorecard + auto-indexes to ChromaDB

    S->>DG: Route → DocGen (review complete)
    DG-->>S: Returns generated README.md

    S->>DP: Route → Deployer (docs complete)
    DP-->>S: Returns Dockerfile, docker-compose, CI/CD

    S->>A: Route → FINISH
    A-->>F: event: complete
    F->>U: Show completed project + Download ZIP
```

---

## 📊 AgentState Schema (Shared State Container)

All 9 agent nodes read from and write to a single shared `AgentState` TypedDict:

```python
class AgentState(TypedDict):
    # Identity
    project_id: str
    user_prompt: str
    selected_model: str
    current_step: str
    active_agent: str

    # Phase 1: Core Generation
    plan: Optional[Dict[str, Any]]              # Planner output
    architecture: Optional[Dict[str, Any]]      # Architect output
    generated_files: List[Dict[str, str]]        # Coder output

    # Phase 2: Self-Healing Loop
    test_results: Optional[Dict[str, Any]]       # Tester output
    debug_reflections: List[Dict[str, Any]]      # Debugger patch history
    review_report: Optional[Dict[str, Any]]      # Reviewer scorecard
    retry_count: int                              # Debug retry counter

    # Phase 3: RAG Memory
    rag_context: List[Dict[str, Any]]             # Retrieved memory snippets

    # Phase 4 & 5: HITL & DevOps
    hitl_approved: bool                           # Human approval flag
    awaiting_approval: bool                       # Pipeline paused state
    docs_generated: List[Dict[str, str]]          # DocGen output
    deployment_files: List[Dict[str, str]]        # Deployer output

    # Shared
    logs: List[Dict[str, Any]]                    # Agent execution logs
    next_node: str                                # Supervisor routing decision
    error: Optional[str]                          # Error state
```

---

## ⚡ Server-Sent Events (SSE) Protocol

Real-time streaming between FastAPI and the React frontend uses JSON-formatted SSE events:

| Event | Emitted By | Payload |
|:---|:---|:---|
| `log` | All agents | `{ agent, message, timestamp }` |
| `status` | Supervisor transitions | `{ current_step, active_agent, file_count, retry_count, ... }` |
| `file_created` | Coder, DocGen, Deployer | `{ path, content }` |
| `file_patched` | Debugger | `{ path, content }` |
| `test_results` | Tester | `{ overall_passed, passed, failed, file_results }` |
| `review_report` | Reviewer | `{ overall_score, quality_score, findings, approved }` |
| `awaiting_approval` | HITL Checkpoint | `{ project_id, architecture }` |
| `complete` | Final node | `{ project_id, status: "COMPLETED" }` |
| `error` | Any failure | `{ error, project_id }` |

---

## 🧠 ChromaDB RAG Memory Architecture

```mermaid
graph LR
    subgraph Episodic["📁 Episodic Memory (Per-Project)"]
        E1["Project A Code Chunks"]
        E2["Project B Code Chunks"]
    end

    subgraph Semantic["🧠 Semantic Memory (Shared)"]
        S1["Design Patterns"]
        S2["Framework Snippets"]
    end

    subgraph Agents["🤖 RAG-Augmented Agents"]
        ARCH["📐 Architect<br/>Retrieves architecture patterns"]
        CODER["💻 Coder<br/>Retrieves code references"]
        REV["📋 Reviewer<br/>Auto-indexes new code"]
    end

    Episodic --> ARCH
    Semantic --> ARCH
    Episodic --> CODER
    Semantic --> CODER
    REV --> Episodic
```

- **Episodic Memory**: Per-project code chunks indexed with 20% overlap, stored with `project_id` metadata.
- **Semantic Memory**: Reusable architecture patterns and framework best practices, shared across all projects.
- **Retrieval**: Cosine similarity search via ChromaDB, injected as context into Architect and Coder LLM prompts.
- **Indexing**: Automatically triggered by the Reviewer Agent after code review completion.

---

## 🛡️ Workspace Sandbox Security

- All generated code is written inside `./workspace/<project_id>/` via `WorkspaceService`.
- Path traversal attacks are prevented by sanitizing all file paths before write operations.
- Subprocess execution for testing is time-limited (15s timeout) and restricted to syntax checking only.
- No network access is granted to generated code during testing.

---

## 🔌 Frontend Component Architecture

```mermaid
graph TB
    App["App.tsx<br/>Main Application"]
    App --> Header["Header.tsx<br/>Nav + Model Selector"]
    App --> Input["ProjectInput.tsx<br/>Prompt Bar"]
    App --> DAG["AgentDAG.tsx<br/>9-Node Pipeline Viz"]
    App --> Logs["LiveLogs.tsx<br/>SSE Event Terminal"]
    App --> Code["CodeViewer.tsx<br/>File Browser + ZIP"]
    App --> Tests["TestResultsPanel.tsx<br/>Test Results"]
    App --> Review["ReviewScoreCard.tsx<br/>Quality Audit"]
    App --> Memory["MemoryViewer.tsx<br/>Vector Search"]
    App --> HITL["HITLApprovalModal.tsx<br/>Approval Gate"]

    style App fill:#6366f1,color:#fff
```

Each component is self-contained with its own state management and SSE event handlers, communicating through React props and the centralized `App.tsx` state.
