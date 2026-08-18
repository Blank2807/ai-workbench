import subprocess
from pathlib import Path
from typing import Any, Dict, List

from modules.ide.tools import workspace_root


def run_git_command(command: List[str], timeout: int = 60) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            cwd=workspace_root(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "success": proc.returncode == 0,
            "command": " ".join(command),
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-20000:],
            "stderr": proc.stderr[-20000:],
        }

    except Exception as e:
        return {
            "success": False,
            "command": " ".join(command),
            "error": str(e),
        }


def git_status() -> Dict[str, Any]:
    return run_git_command(["git", "status", "--short"])


def git_diff() -> Dict[str, Any]:
    return run_git_command(["git", "diff"])


def git_current_branch() -> Dict[str, Any]:
    return run_git_command(["git", "branch", "--show-current"])


def git_create_branch(branch_name: str) -> Dict[str, Any]:
    return run_git_command(["git", "checkout", "-b", branch_name])


def git_add_all() -> Dict[str, Any]:
    return run_git_command(["git", "add", "."])


def git_commit(message: str) -> Dict[str, Any]:
    return run_git_command(["git", "commit", "-m", message])


def git_push(branch_name: str) -> Dict[str, Any]:
    return run_git_command(["git", "push", "-u", "origin", branch_name])


def github_create_pr(title: str, body: str, base: str = "main") -> Dict[str, Any]:
    return run_git_command(
        [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
        ],
        timeout=120,
    )