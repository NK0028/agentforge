import os
import json
import asyncio
import uuid
import zipfile
import io
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, BackgroundTasks, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.graph.workflow import agent_graph
from app.services.workspace import WorkspaceService
from app.services.memory import memory_service

router = APIRouter(prefix="/agent", tags=["Agent Operations"])

class ProjectRunRequest(BaseModel):
    prompt: str
    model: str = "qwen2.5-coder"

class HITLResumeRequest(BaseModel):
    approved: bool = True
    modified_files: Optional[List[Dict[str, str]]] = None  # optional human modifications to files list

PROJECT_STREAMS: Dict[str, asyncio.Queue] = {}
PROJECT_STATES: Dict[str, Dict[str, Any]] = {}


async def run_agent_workflow(project_id: str, prompt: str, model_name: str):
    queue = PROJECT_STREAMS.get(project_id)

    initial_state = {
        "project_id": project_id,
        "user_prompt": prompt,
        "selected_model": model_name,
        "current_step": "init",
        "active_agent": "System",
        "plan": None,
        "architecture": None,
        "generated_files": [],
        "test_results": None,
        "debug_reflections": [],
        "review_report": None,
        "retry_count": 0,
        "rag_context": [],
        "hitl_approved": False,
        "awaiting_approval": False,
        "docs_generated": [],
        "deployment_files": [],
        "logs": [],
        "next_node": "supervisor",
        "error": None
    }

    PROJECT_STATES[project_id] = initial_state

    if queue:
        await queue.put({
            "event": "log",
            "data": json.dumps({
                "agent": "System",
                "message": f"🚀 Initializing AgentForge project session [{project_id}]",
                "timestamp": "now"
            })
        })

    try:
        for output in agent_graph.stream(initial_state):
            for node_name, updated_state in output.items():
                PROJECT_STATES[project_id] = updated_state

                # Stream logs
                for log in updated_state.get("logs", []):
                    if queue:
                        await queue.put({"event": "log", "data": json.dumps(log)})

                # Stream execution status
                if queue:
                    await queue.put({
                        "event": "status",
                        "data": json.dumps({
                            "current_step": updated_state.get("current_step"),
                            "active_agent": updated_state.get("active_agent"),
                            "awaiting_approval": updated_state.get("awaiting_approval", False),
                            "plan": updated_state.get("plan"),
                            "architecture": updated_state.get("architecture"),
                            "file_count": len(updated_state.get("generated_files", [])),
                            "retry_count": updated_state.get("retry_count", 0),
                            "test_results": updated_state.get("test_results"),
                            "review_report": updated_state.get("review_report")
                        })
                    })

                # If state paused at HITL checkpoint
                if updated_state.get("awaiting_approval"):
                    if queue:
                        await queue.put({
                            "event": "awaiting_approval",
                            "data": json.dumps({
                                "project_id": project_id,
                                "architecture": updated_state.get("architecture")
                            })
                        })
                    return

                # Stream files
                if node_name in ["coder", "docgen", "deployer"]:
                    for f in updated_state.get("generated_files", []):
                        if queue:
                            await queue.put({
                                "event": "file_created",
                                "data": json.dumps({"path": f["path"], "content": f["content"]})
                            })

                if node_name == "debugger":
                    for f in updated_state.get("generated_files", []):
                        if queue:
                            await queue.put({
                                "event": "file_patched",
                                "data": json.dumps({"path": f["path"], "content": f["content"]})
                            })

        if queue:
            await queue.put({
                "event": "complete",
                "data": json.dumps({"project_id": project_id, "status": "COMPLETED"})
            })

    except Exception as e:
        if queue:
            await queue.put({
                "event": "error",
                "data": json.dumps({"error": str(e), "project_id": project_id})
            })


@router.post("/run")
async def start_project(req: ProjectRunRequest, bg_tasks: BackgroundTasks):
    project_id = str(uuid.uuid4())[:8]
    PROJECT_STREAMS[project_id] = asyncio.Queue()
    bg_tasks.add_task(run_agent_workflow, project_id, req.prompt, req.model)
    return {
        "project_id": project_id,
        "status": "QUEUED",
        "stream_url": f"/api/agent/stream/{project_id}"
    }


@router.post("/resume/{project_id}")
async def resume_project(project_id: str, req: HITLResumeRequest, bg_tasks: BackgroundTasks):
    """
    Resumes graph execution after Human-In-The-Loop approval.
    """
    state = PROJECT_STATES.get(project_id)
    if not state:
        raise HTTPException(status_code=404, detail="Project session not found.")

    if not req.approved:
        state["logs"].append({
            "agent": "System",
            "message": "❌ Human Developer rejected current architecture design.",
            "timestamp": "now"
        })
        return {"status": "REJECTED"}

    # Apply human modifications if provided
    if req.modified_files and state.get("architecture"):
        state["architecture"]["files"] = req.modified_files

    state["hitl_approved"] = True
    state["awaiting_approval"] = False

    queue = PROJECT_STREAMS.get(project_id)
    if queue:
        await queue.put({
            "event": "log",
            "data": json.dumps({
                "agent": "HumanDeveloper",
                "message": "✅ Architecture approved by Human Developer. Resuming pipeline execution...",
                "timestamp": "now"
            })
        })

    # Continue streaming from active state
    bg_tasks.add_task(resume_agent_workflow, project_id, state)

    return {"project_id": project_id, "status": "RESUMED"}


async def resume_agent_workflow(project_id: str, current_state: Dict[str, Any]):
    queue = PROJECT_STREAMS.get(project_id)
    try:
        for output in agent_graph.stream(current_state):
            for node_name, updated_state in output.items():
                PROJECT_STATES[project_id] = updated_state

                for log in updated_state.get("logs", []):
                    if queue:
                        await queue.put({"event": "log", "data": json.dumps(log)})

                if queue:
                    await queue.put({
                        "event": "status",
                        "data": json.dumps({
                            "current_step": updated_state.get("current_step"),
                            "active_agent": updated_state.get("active_agent"),
                            "plan": updated_state.get("plan"),
                            "architecture": updated_state.get("architecture"),
                            "file_count": len(updated_state.get("generated_files", [])),
                            "retry_count": updated_state.get("retry_count", 0),
                            "test_results": updated_state.get("test_results"),
                            "review_report": updated_state.get("review_report")
                        })
                    })

                if node_name in ["coder", "docgen", "deployer"]:
                    for f in updated_state.get("generated_files", []):
                        if queue:
                            await queue.put({
                                "event": "file_created",
                                "data": json.dumps({"path": f["path"], "content": f["content"]})
                            })

        if queue:
            await queue.put({
                "event": "complete",
                "data": json.dumps({"project_id": project_id, "status": "COMPLETED"})
            })
    except Exception as e:
        if queue:
            await queue.put({
                "event": "error",
                "data": json.dumps({"error": str(e), "project_id": project_id})
            })


@router.get("/stream/{project_id}")
async def stream_project_events(project_id: str):
    queue = PROJECT_STREAMS.get(project_id)
    if not queue:
        queue = asyncio.Queue()
        PROJECT_STREAMS[project_id] = queue

    async def event_generator():
        while True:
            event = await queue.get()
            yield event
            if event.get("event") in ["complete", "error"]:
                break

    return EventSourceResponse(event_generator())


@router.get("/workspace/{project_id}")
async def get_workspace_files(project_id: str):
    service = WorkspaceService(project_id=project_id)
    return {"project_id": project_id, "files": service.list_files()}


@router.get("/export/{project_id}")
async def export_project_zip(project_id: str):
    """
    One-click ZIP download endpoint of the generated application repository.
    """
    service = WorkspaceService(project_id=project_id)
    files = service.list_files()

    if not files:
        raise HTTPException(status_code=404, detail="No workspace files generated yet.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            zip_file.writestr(file["path"], file["content"])

    zip_buffer.seek(0)
    filename = f"agentforge-{project_id}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/memory/stats")
async def get_memory_stats():
    return memory_service.get_stats()


@router.get("/memory/search")
async def search_memory(q: str = Query(..., min_length=1), n: int = 5):
    hits = memory_service.retrieve(query=q, n_results=n)
    return {"query": q, "results_count": len(hits), "hits": hits}
