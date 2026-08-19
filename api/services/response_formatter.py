from typing import Any, Dict, List


def format_command_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic formatter for command outputs.
    Keeps raw output but adds frontend-friendly summary fields.
    """

    success = result.get("success", False)
    command = result.get("command", "")
    stdout = result.get("stdout", "") or ""
    stderr = result.get("stderr", "") or ""
    error = result.get("error", "") or ""

    if success:
        summary = "Command completed successfully."
        status = "success"
    else:
        summary = "Command failed."
        status = "failed"

    if stderr:
        summary = stderr.strip().splitlines()[0]

    if error:
        summary = str(error)

    return {
        "success": success,
        "status": status,
        "summary": summary,
        "command": command,
        "raw": result,
    }


def format_git_status(result: Dict[str, Any]) -> Dict[str, Any]:
    stdout = result.get("stdout", "") or ""
    lines = [line for line in stdout.splitlines() if line.strip()]

    changed_files: List[Dict[str, str]] = []

    for line in lines:
        status_code = line[:2].strip()
        file_path = line[3:].strip() if len(line) > 3 else ""

        changed_files.append(
            {
                "status_code": status_code,
                "path": file_path,
            }
        )

    if not changed_files:
        summary = "Working tree is clean."
        status = "clean"
    else:
        summary = f"{len(changed_files)} changed file(s) found."
        status = "changes_found"

    return {
        "success": result.get("success", False),
        "status": status,
        "summary": summary,
        "changed_file_count": len(changed_files),
        "changed_files": changed_files,
        "raw": result,
    }


def format_pr_checks(result: Dict[str, Any]) -> Dict[str, Any]:
    stdout = result.get("stdout", "") or ""
    lines = [line for line in stdout.splitlines() if line.strip()]
    checks: List[Dict[str, str]] = []
    for line in lines:
        parts = line.split("\t")

        if len(parts) >= 2:
            checks.append(
                {
                    "name": parts[0],
                    "result": parts[1],
                    "duration": parts[2] if len(parts) > 2 else "",
                    "url": parts[3] if len(parts) > 3 else "",
                }
            )

    failed = [check for check in checks if check["result"] in {"fail", "failed"}]
    pending = [check for check in checks if check["result"] in {"pending", "queued", "in_progress"}]

    if failed:
        status = "failed"
        summary = f"{len(failed)} PR check(s) failed."
    elif pending:
        status = "pending"
        summary = f"{len(pending)} PR check(s) pending."
    elif checks:
        status = "passed"
        summary = "All PR checks passed."
    else:
        status = "unknown"
        summary = "No PR checks found."

    return {
        "success": result.get("success", False),
        "status": status,
        "summary": summary,
        "check_count": len(checks),
        "checks": checks,
        "raw": result,
    }


def format_test_result(result: Dict[str, Any]) -> Dict[str, Any]:
    stdout = result.get("stdout", "") or ""
    stderr = result.get("stderr", "") or ""

    passed_count = 0
    failed_count = 0

    for line in stdout.splitlines():
        if " passed" in line and "failed" not in line:
            parts = line.strip().split()
            for idx, part in enumerate(parts):
                if part == "passed" and idx > 0 and parts[idx - 1].isdigit():
                    passed_count = int(parts[idx - 1])

        if " failed" in line:
            parts = line.strip().replace(",", "").split()
            for idx, part in enumerate(parts):
                if part == "failed" and idx > 0 and parts[idx - 1].isdigit():
                    failed_count = int(parts[idx - 1])

    success = result.get("success", False)

    if success:
        status = "passed"
        summary = "Tests passed successfully."
    else:
        status = "failed"
        summary = "Tests failed."

    if stderr:
        summary = stderr.strip().splitlines()[0]

    return {
        "success": success,
        "status": status,
        "summary": summary,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "command": result.get("command", ""),
        "raw": result,
    }