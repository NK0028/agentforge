# Contributing to AgentForge 🤝

Thank you for your interest in contributing to AgentForge! This guide will help you get started.

---

## 🏗️ Development Setup

### Prerequisites

| Requirement | Version |
|:---|:---|
| Python | 3.10+ |
| Node.js | 18+ |
| Ollama | Latest ([ollama.com](https://ollama.com)) |
| Git | Latest |

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/agentforge.git
cd agentforge
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Pull an Ollama Model

```bash
ollama pull qwen2.5-coder
```

---

## 📐 Architecture Overview

Before contributing, please read the [Architecture Documentation](docs/ARCHITECTURE.md) to understand:

- The 9-Node LangGraph agent pipeline
- Shared `AgentState` TypedDict pattern
- SSE event streaming protocol
- ChromaDB RAG memory architecture
- Workspace sandbox security model

---

## 🔀 Contribution Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below.

3. **Test your changes**:
   ```bash
   # Backend — verify all modules compile
   cd backend
   python -m py_compile app/agents/YOUR_MODULE.py

   # Frontend — verify TypeScript + build
   cd frontend
   npm run build
   ```

4. **Commit with descriptive messages**:
   ```bash
   git commit -m "feat(agent): add semantic caching to Architect node"
   ```

5. **Push and open a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## 📝 Code Style Guidelines

### Python (Backend)

- **Type hints** on all function signatures.
- **Docstrings** on all public functions and classes.
- Use `logging` module — no `print()` statements.
- All file I/O must go through `WorkspaceService` — never write to raw paths.
- LLM calls must handle JSON parsing failures gracefully with fallback responses.
- Maximum function length: ~50 lines. Extract helpers for readability.

### TypeScript (Frontend)

- Explicit type annotations on props interfaces.
- Components should be functional (`React.FC<Props>`).
- Use Lucide React icons — no inline SVGs.
- CSS: Use TailwindCSS utility classes and the existing `glass-panel`, `bg-dark-*`, `text-brand-*` design tokens.
- State management stays in `App.tsx` — components receive state via props.

### Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to Use |
|:---|:---|
| `feat` | New feature or agent node |
| `fix` | Bug fix |
| `docs` | Documentation updates |
| `refactor` | Code restructuring without behavior change |
| `style` | Formatting, whitespace, UI polish |
| `test` | Adding or updating tests |
| `chore` | Build scripts, dependencies, tooling |

---

## 🗺️ Areas Open for Contribution

### 🟢 Beginner-Friendly

- Add more detailed error messages to agent fallback handlers
- Improve CSS animations and micro-interactions on dashboard components
- Add dark/light theme toggle support
- Write unit tests for `WorkspaceService` and `MemoryService`

### 🟡 Intermediate

- Add a **Benchmarking Agent** that runs performance profiling on generated code
- Implement **multi-project session management** (switch between active projects)
- Add **code diff viewer** showing before/after debugger patches
- Add WebSocket support as alternative to SSE

### 🔴 Advanced

- Integrate **CrewAI** or **AutoGen** as alternative orchestration backends
- Add **multi-modal support** (image → UI code generation)
- Implement **distributed agent execution** across multiple machines
- Add **fine-tuning pipeline** for project-specific code quality models

---

## 🐛 Reporting Issues

When reporting bugs, please include:

1. **Steps to reproduce** the issue
2. **Expected behavior** vs actual behavior
3. **Browser and OS** information
4. **Ollama model** being used
5. **Console logs** (browser dev tools + backend terminal)

---

## 📄 License

By contributing to AgentForge, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for helping make AgentForge better! 🚀
