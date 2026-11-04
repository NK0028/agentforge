import json
import logging
from app.graph.state import AgentState
from app.services.workspace import WorkspaceService

logger = logging.getLogger(__name__)

def deployer_node(state: AgentState) -> AgentState:
    """
    Deployment Agent: Generates production Dockerfile, docker-compose.yml,
    and GitHub Actions CI/CD workflow for the created application.
    """
    logger.info("--- DEPLOYMENT AGENT ---")
    state["active_agent"] = "Deployer"
    state["current_step"] = "deployment"

    workspace = WorkspaceService(project_id=state["project_id"])
    plan = state.get("plan", {})
    tech_stack = plan.get("tech_stack", {})
    backend_type = tech_stack.get("backend", "").lower()

    # Generate Dockerfile based on stack
    if "python" in backend_type or "fastapi" in backend_type:
        dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
EXPOSE 8000
CMD ["python3", "main.py"]
"""
    else:
        dockerfile_content = """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install || true
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
"""

    docker_compose_content = """version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
"""

    github_action_content = """name: CI Build & Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
"""

    # Save deployment files to workspace
    f1 = workspace.write_file("Dockerfile", dockerfile_content)
    f2 = workspace.write_file("docker-compose.yml", docker_compose_content)
    f3 = workspace.write_file(".github/workflows/ci.yml", github_action_content)

    deployment_files = [
        {"path": f1, "content": dockerfile_content},
        {"path": f2, "content": docker_compose_content},
        {"path": f3, "content": github_action_content}
    ]

    state["deployment_files"] = deployment_files

    # Append to generated_files for UI viewing
    for df in deployment_files:
        state["generated_files"].append(df)

    state["logs"].append({
        "agent": "Deployer",
        "message": f"🐳 Generated DevOps deployment manifests: Dockerfile, docker-compose.yml, CI/CD pipeline.",
        "timestamp": "now"
    })

    return state
