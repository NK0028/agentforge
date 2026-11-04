# AgentForge: Multi-Phase Project Roadmap 🗺️

AgentForge is developed iteratively following a production-grade open-source roadmap. All 5 core phases are fully completed.

---

## 🎯 Phase 1: MVP Core Foundation (Completed ✅)

### Objectives
- Establish local-first multi-agent architecture using **LangGraph**, **FastAPI**, and **React**.
- Implement the core 4-Agent pipeline: Supervisor, Planner, Architect, and Coder.
- Provide a modern dark UI with visual pipeline DAG, live event terminal logs, and generated workspace code viewer.
- Full Ollama integration supporting local models (`qwen2.5-coder`, `deepseek-r1`, `llama3.1`, etc.).

### Deliverables
- [x] LangGraph State Graph engine with Supervisor routing.
- [x] FastAPI server with SSE streaming endpoints for real-time thoughts & code.
- [x] React + TypeScript + Vite + TailwindCSS interactive dashboard.
- [x] Workspace File System service for saving generated code to disk.
- [x] Open-source documentation suite (`docs/`).

---

## 🚀 Phase 2: Autonomous Testing & Reflection Loop (Completed ✅)

### Objectives
- Introduce the **Testing Agent** (`tester.py`), **Debug/Fix Agent** (`debugger.py`), and **Reviewer Agent** (`reviewer.py`).
- Self-correcting execution loop: If generated code fails syntax validation, automatically route back to the Debug Agent for root cause analysis and surgical fixes (max 3 retries).
- Automated code quality, security, and completeness audit with 4-metric scorecards.

### Deliverables
- [x] Isolated python/node code execution sandbox (`py_compile` & `node --check`).
- [x] Test runner node executing sandboxed syntax checks.
- [x] LangGraph conditional self-healing loop: `Coder -> Tester -> (Pass? -> Reviewer | Fail? -> Debugger -> Tester)`.
- [x] TestResultsPanel & ReviewScoreCard components in frontend dashboard.
- [x] Audit report with auto-indexing trigger for long-term memory.

---

## 🧠 Phase 3: Long-Term Memory & RAG Knowledge Base (Completed ✅)

### Objectives
- Add ChromaDB vector store integration for codebase RAG and developer preferences memory.
- Enable Agents to search existing repositories and leverage standard architectural patterns.

### Deliverables
- [x] ChromaDB indexing service (`memory.py`) for local code repositories.
- [x] Episodic & Semantic memory storage per project workspace.
- [x] Retrieval-Augmented Generation (RAG) injection for Architect & Coder agents.
- [x] MemoryViewer UI component & vector search API endpoints (`/api/agent/memory/stats`, `/api/agent/memory/search`).

---

## 🤝 Phase 4: Human-In-The-Loop (HITL) & Interrupt Support (Completed ✅)

### Objectives
- Give human developers control over agent execution milestones.
- Allow human intervention at key checkpoints (e.g. approve software architecture plan before coding begins).

### Deliverables
- [x] LangGraph `PAUSE_HITL` checkpoint integration in Supervisor router.
- [x] Frontend HITL approval modal (`HITLApprovalModal.tsx`) to review and edit architecture specs.
- [x] Resume execution state endpoint (`/api/agent/resume/{project_id}`) in FastAPI.

---

## 📦 Phase 5: Documentation & DevOps Automation (Completed ✅)

### Objectives
- Automate complete project packaging, Dockerfile creation, CI/CD pipeline generation, and comprehensive README creation.

### Deliverables
- [x] Documentation Agent (`docgen.py`) creating complete project documentation and API specs.
- [x] Deployment Agent (`deployer.py`) generating Dockerfiles, docker-compose configs, and GitHub Actions workflows.
- [x] One-click ZIP repository export endpoint (`/api/agent/export/{project_id}`).
- [x] Clean one-click ZIP download button in CodeViewer UI.

---

## 🔮 Future Roadmap (Phase 6 & Beyond)

- [ ] Multi-project tabbed workspace switcher.
- [ ] Pytest / Jest unit test execution in isolated Docker container sandboxes.
- [ ] Git commit & push automation to GitHub repositories directly from UI.
- [ ] Multi-modal prompt support (sketch/mockup image to UI code).
