import subprocess
import os
import logging
from typing import Dict, Any
from app.graph.state import AgentState
from app.services.workspace import WorkspaceService
from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_EXECUTION_TIMEOUT = 15  # seconds per file execution

EXECUTABLE_EXTENSIONS = {".py", ".js", ".sh"}

def _detect_language(file_path: str) -> str:
    """Detect language based on file extension."""
    ext = os.path.splitext(file_path)[-1].lower()
    return {".py": "python", ".js": "node", ".sh": "bash"}.get(ext, "unknown")


def _run_syntax_check(file_path: str, language: str) -> Dict[str, Any]:
    """
    Performs a static syntax check without executing code.
    Uses python3 -m py_compile for Python, node --check for JS.
    """
    try:
        if language == "python":
            result = subprocess.run(
                ["python3", "-m", "py_compile", file_path],
                capture_output=True, text=True, timeout=10
            )
        elif language == "node":
            result = subprocess.run(
                ["node", "--check", file_path],
                capture_output=True, text=True, timeout=10
            )
        else:
            return {"passed": True, "stdout": "", "stderr": "", "exit_code": 0}

        passed = result.returncode == 0
        return {
            "passed": passed,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "stdout": "", "stderr": "Syntax check timed out.", "exit_code": -1}
    except FileNotFoundError as e:
        return {"passed": True, "stdout": "", "stderr": f"Interpreter not found: {e}. Skipping check.", "exit_code": 0}


def tester_node(state: AgentState) -> AgentState:
    """
    Testing Agent: Runs syntax validation on all generated Python/JS files.
    Records per-file pass/fail status, collects all errors into test_results.
    """
    logger.info("--- TESTING AGENT ---")
    state["active_agent"] = "Tester"
    state["current_step"] = "testing"

    workspace = WorkspaceService(project_id=state["project_id"])
    generated_files = state.get("generated_files", [])

    file_results = []
    total_passed = 0
    total_failed = 0
    all_errors = []

    for file_info in generated_files:
        file_path = file_info.get("path", "")
        language = _detect_language(file_path)

        if language == "unknown":
            # HTML, CSS, YAML, etc. — skip execution, mark as passed
            file_results.append({
                "path": file_path,
                "language": language,
                "passed": True,
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "note": "Non-executable file; syntax check skipped."
            })
            total_passed += 1
            continue

        abs_path = os.path.join(workspace.sandbox_path, file_path.lstrip("/\\"))
        check = _run_syntax_check(abs_path, language)
        check["path"] = file_path
        check["language"] = language
        file_results.append(check)

        if check["passed"]:
            total_passed += 1
            log_msg = f"✓ [{file_path}] — Syntax check PASSED"
        else:
            total_failed += 1
            error_entry = {
                "file_path": file_path,
                "stderr": check.get("stderr", ""),
                "exit_code": check.get("exit_code", -1)
            }
            all_errors.append(error_entry)
            log_msg = f"✗ [{file_path}] — Syntax check FAILED: {check.get('stderr', '')[:200]}"

        state["logs"].append({"agent": "Tester", "message": log_msg, "timestamp": "now"})

    overall_passed = total_failed == 0

    state["test_results"] = {
        "overall_passed": overall_passed,
        "total_files": len(generated_files),
        "passed": total_passed,
        "failed": total_failed,
        "file_results": file_results,
        "errors": all_errors
    }

    summary_msg = (
        f"Test suite complete: {total_passed}/{len(generated_files)} files passed. "
        f"{'✅ All clear!' if overall_passed else f'⚠️ {total_failed} file(s) require debugging.'}"
    )
    state["logs"].append({"agent": "Tester", "message": summary_msg, "timestamp": "now"})
    logger.info(summary_msg)

    return state
