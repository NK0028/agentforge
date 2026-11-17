import os
import json
import logging
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
from app.core.utils import get_timestamp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent Operations"])

class ProjectRunRequest(BaseModel):
    prompt: str
    model: str = "qwen2.5-coder"

class HITLResumeRequest(BaseModel):
    approved: bool = True
    modified_files: Optional[List[Dict[str, str]]] = None  # optional human modifications to files list

PROJECT_STREAMS: Dict[str, asyncio.Queue] = {}
PROJECT_STATES: Dict[str, Dict[str, Any]] = {}


async def _stream_workflow(project_id: str, state_input: Dict[str, Any]):
    """
    Core execution loop for LangGraph multi-agent pipeline.
    Maintains full cumulative state, deduplicates log/file events,
    and streams structured SSE events to connected frontend clients.
    """
    queue = PROJECT_STREAMS.get(project_id)
    current_state = dict(state_input)
    PROJECT_STATES[project_id] = current_state

    # Track indexes to only broadcast NEW logs and NEW files
    last_log_idx = len(current_state.get("logs", []))
    emitted_file_paths = {f["path"] for f in current_state.get("generated_files", [])}

    try:
        # stream() yields {node_name: node_output_delta}
        for output in agent_graph.stream(current_state):
            for node_name, delta in output.items():
                if isinstance(delta, dict):
                    current_state.update(delta)
                PROJECT_STATES[project_id] = current_state

                # 1. Stream ONLY new logs (fixes O(n^2) log broadcast bug)
                all_logs = current_state.get("logs", [])
                new_logs = all_logs[last_log_idx:]
                for log in new_logs:
                    if queue:
                        await queue.put({"event": "log", "data": json.dumps(log)})
                last_log_idx = len(all_logs)

                # 2. Stream comprehensive status snapshot
                if queue:
                    await queue.put({
                        "event": "status",
                        "data": json.dumps({
                            "current_step": current_state.get("current_step"),
                            "active_agent": current_state.get("active_agent"),
                            "awaiting_approval": current_state.get("awaiting_approval", False),
                            "plan": current_state.get("plan"),
                            "architecture": current_state.get("architecture"),
                            "file_count": len(current_state.get("generated_files", [])),
                            "retry_count": current_state.get("retry_count", 0),
                            "test_results": current_state.get("test_results"),
                            "review_report": current_state.get("review_report")
                        })
                    })

                # 3. Dedicated test_results event
                if node_name == "tester" and current_state.get("test_results"):
                    if queue:
                        await queue.put({
                            "event": "test_results",
                            "data": json.dumps(current_state["test_results"])
                        })

                # 4. Dedicated review_report event
                if node_name == "reviewer" and current_state.get("review_report"):
                    if queue:
                        await queue.put({
                            "event": "review_report",
                            "data": json.dumps(current_state["review_report"])
                        })

                # 5. Handle Human-In-The-Loop pause condition
                if current_state.get("awaiting_approval"):
                    if queue:
                        await queue.put({
                            "event": "awaiting_approval",
                            "data": json.dumps({
                                "project_id": project_id,
                                "architecture": current_state.get("architecture")
                            })
                        })
                    return  # Yield control back to await HITL resume API call

                # 6. Stream only NEW files (fixes duplicate file broadcast bug)
                if node_name in ["coder", "docgen", "deployer"]:
                    for f in current_state.get("generated_files", []):
                        if f["path"] not in emitted_file_paths:
                            emitted_file_paths.add(f["path"])
                            if queue:
                                await queue.put({
                                    "event": "file_created",
                                    "data": json.dumps({"path": f["path"], "content": f["content"]})
                                })

                # 7. Stream patched files on debugger output
                if node_name == "debugger":
                    for f in current_state.get("generated_files", []):
                        if queue:
                            await queue.put({
                                "event": "file_patched",
                                "data": json.dumps({"path": f["path"], "content": f["content"]})
                            })

        # Pipeline completed successfully
        if not current_state.get("awaiting_approval"):
            if queue:
                await queue.put({
                    "event": "complete",
                    "data": json.dumps({"project_id": project_id, "status": "COMPLETED"})
                })

    except Exception as e:
        logger.error(f"Error executing agent workflow for [{project_id}]: {e}", exc_info=True)
        if queue:
            await queue.put({
                "event": "error",
                "data": json.dumps({"error": str(e), "project_id": project_id})
            })


async def run_agent_workflow(project_id: str, prompt: str, model_name: str):
    queue = PROJECT_STREAMS.get(project_id)

    initial_log = {
        "agent": "System",
        "message": f"🚀 Initializing AgentForge project session [{project_id}]",
        "timestamp": get_timestamp()
    }

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
        "logs": [initial_log],
        "next_node": "supervisor",
        "error": None
    }

    PROJECT_STATES[project_id] = initial_state

    if queue:
        await queue.put({
            "event": "log",
            "data": json.dumps(initial_log)
        })

    await _stream_workflow(project_id, initial_state)


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
            "timestamp": get_timestamp()
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
                "timestamp": get_timestamp()
            })
        })

    # Continue streaming from active state
    bg_tasks.add_task(resume_agent_workflow, project_id, state)

    return {"project_id": project_id, "status": "RESUMED"}


async def resume_agent_workflow(project_id: str, current_state: Dict[str, Any]):
    await _stream_workflow(project_id, current_state)


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
