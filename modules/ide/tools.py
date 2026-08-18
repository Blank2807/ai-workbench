import subprocess
import tkinter as tk
import sys

from pathlib import Path
from typing import Any, Dict, List, Optional
from tkinter import filedialog


ROOT_DIR = Path(__file__).resolve().parents[2]

WORKSPACE_STATE = {
    "workspace_root": ROOT_DIR,
    "active_file": None,
    "active_folder": ".",
}


EXCLUDED_DIRS = {
    ".git",
    ".env",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "generated_tests",
}


TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".html", ".css", ".scss", ".sass",
    ".json", ".xml", ".yaml", ".yml",
    ".md", ".txt",
    ".java", ".cs", ".php", ".go", ".rs",
    ".sql", ".sh", ".bat", ".ps1",
    ".ini", ".cfg", ".toml",
}


LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript_react",
    ".ts": "typescript",
    ".tsx": "typescript_react",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".txt": "text",
    ".java": "java",
    ".cs": "csharp",
    ".php": "php",
    ".go": "go",
    ".rs": "rust",
    ".sql": "sql",
    ".sh": "shell",
    ".bat": "batch",
    ".ps1": "powershell",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "config",
}


def workspace_root() -> Path:
    return Path(WORKSPACE_STATE["workspace_root"]).resolve()


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/").strip()


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def is_safe_path(path: Path) -> bool:
    try:
        path.resolve().relative_to(workspace_root())
        return True
    except ValueError:
        return False


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.suffix == ""


def relative_to_workspace(path: Path) -> str:
    return normalize_path(path.resolve().relative_to(workspace_root()))


def detect_language_by_path(path: str) -> Dict[str, Any]:
    requested = normalize_path(path)
    suffix = Path(requested).suffix.lower()

    return {
        "success": True,
        "path": requested,
        "extension": suffix,
        "language": LANGUAGE_BY_EXTENSION.get(suffix, "unknown"),
        "is_supported_text_file": suffix in TEXT_EXTENSIONS or suffix == "",
    }


def pick_file() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    selected = filedialog.askopenfilename(
        title="Select a file",
        initialdir=str(workspace_root()),
        filetypes=[
            ("Code files", "*.py *.js *.jsx *.ts *.tsx *.html *.css *.json *.java *.cs *.php *.sql *.md *.txt"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()
    return selected


def pick_folder() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    selected = filedialog.askdirectory(
        title="Select a workspace folder",
        initialdir=str(workspace_root()),
    )

    root.destroy()
    return selected


def set_workspace(path: str) -> Dict[str, Any]:
    """
    Set the active workspace root folder.
    This allows opening another project folder like an IDE.
    """

    requested = str(path or "").strip()

    if not requested:
        return {
            "success": False,
            "error_code": "MISSING_PATH",
            "error": "Workspace folder path is required.",
        }

    folder_path = Path(requested).expanduser().resolve()

    if not folder_path.exists():
        return {
            "success": False,
            "error_code": "FOLDER_NOT_FOUND",
            "error": f"Folder not found: {requested}",
        }

    if not folder_path.is_dir():
        return {
            "success": False,
            "error_code": "NOT_A_FOLDER",
            "error": f"Path is not a folder: {requested}",
        }

    WORKSPACE_STATE["workspace_root"] = folder_path
    WORKSPACE_STATE["active_file"] = None
    WORKSPACE_STATE["active_folder"] = "."

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "active_file": None,
        "active_folder": ".",
        "message": "Workspace folder opened successfully.",
    }


def select_workspace_folder() -> Dict[str, Any]:
    """
    Open a folder picker and set selected folder as workspace.
    """

    selected = pick_folder()

    if not selected:
        return {
            "success": False,
            "error_code": "NO_FOLDER_SELECTED",
            "error": "No folder was selected.",
        }

    return set_workspace(selected)


def select_file_dialog() -> Dict[str, Any]:
    """
    Open a file picker dialog and set selected file as active file.
    """

    selected = pick_file()

    if not selected:
        return {
            "success": False,
            "error_code": "NO_FILE_SELECTED",
            "error": "No file was selected.",
        }

    try:
        selected_path = Path(selected).resolve()

        # If selected file is outside current workspace, switch workspace to its parent folder
        if not is_safe_path(selected_path):
            WORKSPACE_STATE["workspace_root"] = selected_path.parent
            WORKSPACE_STATE["active_folder"] = "."
            WORKSPACE_STATE["active_file"] = None

        relative_path = relative_to_workspace(selected_path)

        return open_file(relative_path)

    except Exception as e:
        return {
            "success": False,
            "error_code": "SELECT_FILE_ERROR",
            "error": str(e),
            "selected": selected,
        }

    
def get_workspace_context() -> Dict[str, Any]:
    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "active_file": WORKSPACE_STATE.get("active_file"),
        "active_folder": WORKSPACE_STATE.get("active_folder"),
    }


def clear_active_context() -> Dict[str, Any]:
    WORKSPACE_STATE["active_file"] = None
    WORKSPACE_STATE["active_folder"] = "."

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "active_file": None,
        "active_folder": ".",
        "message": "Active file and folder context cleared.",
    }


def find_file_recursively(path: str) -> Dict[str, Any]:
    requested = normalize_path(path)

    if not requested:
        active_file = WORKSPACE_STATE.get("active_file")

        if active_file:
            requested = active_file
        else:
            return {
                "success": False,
                "error_code": "MISSING_PATH",
                "error": "File path is required and no active file is set.",
            }

    exact_path = (workspace_root() / requested).resolve()

    if exact_path.exists() and exact_path.is_file() and is_safe_path(exact_path):
        return {
            "success": True,
            "path": exact_path,
            "relative_path": relative_to_workspace(exact_path),
            "match_type": "exact",
        }

    requested_name = Path(requested).name.lower()
    matches: List[Path] = []

    for file_path in workspace_root().rglob("*"):
        if is_excluded(file_path):
            continue

        if not file_path.is_file():
            continue

        if file_path.name.lower() == requested_name:
            matches.append(file_path)

    if len(matches) == 1:
        matched = matches[0].resolve()

        return {
            "success": True,
            "path": matched,
            "relative_path": relative_to_workspace(matched),
            "match_type": "recursive_filename",
        }

    if len(matches) > 1:
        return {
            "success": False,
            "error_code": "AMBIGUOUS_FILE",
            "error": f"Multiple files found for filename: {path}",
            "requested_path": path,
            "possible_matches": [
                relative_to_workspace(match)
                for match in matches
            ],
        }

    return {
        "success": False,
        "error_code": "FILE_NOT_FOUND",
        "error": f"File not found: {path}",
        "requested_path": path,
    }


def resolve_project_path(path: str = ".") -> Dict[str, Any]:
    requested = normalize_path(path or ".")

    if requested in {"", "."}:
        active_folder = WORKSPACE_STATE.get("active_folder") or "."
        requested = active_folder

    exact_path = (workspace_root() / requested).resolve()

    if exact_path.exists() and is_safe_path(exact_path):
        return {
            "success": True,
            "path": exact_path,
            "relative_path": relative_to_workspace(exact_path) if exact_path != workspace_root() else ".",
            "type": "directory" if exact_path.is_dir() else "file",
        }

    file_result = find_file_recursively(requested)

    if file_result.get("success"):
        return {
            "success": True,
            "path": file_result["path"],
            "relative_path": file_result["relative_path"],
            "type": "file",
        }

    return file_result


def open_file(path: str) -> Dict[str, Any]:
    """
    Set a file as the active file.
    """

    result = find_file_recursively(path)

    if not result.get("success"):
        return result

    file_path: Path = result["path"]

    if not is_text_file(file_path):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_FILE_TYPE",
            "error": "Only text/code files can be opened as active file.",
            "path": result["relative_path"],
            "extension": file_path.suffix,
        }

    WORKSPACE_STATE["active_file"] = result["relative_path"]
    WORKSPACE_STATE["active_folder"] = normalize_path(Path(result["relative_path"]).parent)

    if WORKSPACE_STATE["active_folder"] == ".":
        WORKSPACE_STATE["active_folder"] = "."

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "active_file": WORKSPACE_STATE["active_file"],
        "active_folder": WORKSPACE_STATE["active_folder"],
        "language": LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower(), "unknown"),
        "message": "File opened and set as active file.",
    }


def open_folder(path: str) -> Dict[str, Any]:
    """
    Set a folder as the active folder inside current workspace.
    """

    resolved = resolve_project_path(path)

    if not resolved.get("success"):
        return resolved

    folder_path: Path = resolved["path"]

    if not folder_path.is_dir():
        return {
            "success": False,
            "error_code": "NOT_A_FOLDER",
            "error": "The given path is not a folder.",
            "path": resolved["relative_path"],
        }

    WORKSPACE_STATE["active_folder"] = resolved["relative_path"]
    WORKSPACE_STATE["active_file"] = None

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "active_folder": WORKSPACE_STATE["active_folder"],
        "active_file": None,
        "message": "Folder opened and set as active folder.",
    }


def list_files(path: str = ".") -> Dict[str, Any]:
    resolved = resolve_project_path(path)

    if not resolved.get("success"):
        return resolved

    base_path: Path = resolved["path"]

    if base_path.is_file():
        return {
            "success": True,
            "workspace_root": str(workspace_root()),
            "base_path": resolved["relative_path"],
            "file_count": 1,
            "files": [resolved["relative_path"]],
        }

    files: List[str] = []

    for file_path in base_path.rglob("*"):
        if is_excluded(file_path):
            continue

        if file_path.is_file():
            files.append(relative_to_workspace(file_path))

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "base_path": resolved["relative_path"],
        "file_count": len(files),
        "files": sorted(files),
    }


def list_code_files(path: str = ".") -> Dict[str, Any]:
    result = list_files(path)

    if not result.get("success"):
        return result

    code_files = []

    for file in result["files"]:
        suffix = Path(file).suffix.lower()

        if suffix in TEXT_EXTENSIONS:
            code_files.append(
                {
                    "path": file,
                    "extension": suffix,
                    "language": LANGUAGE_BY_EXTENSION.get(suffix, "unknown"),
                }
            )

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "base_path": result["base_path"],
        "file_count": len(code_files),
        "files": code_files,
    }


def read_file(path: str = "", max_chars: int = 30000) -> Dict[str, Any]:
    result = find_file_recursively(path)

    if not result.get("success"):
        return result

    file_path: Path = result["path"]

    if not is_text_file(file_path):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_FILE_TYPE",
            "error": "Only text/code files can be read.",
            "path": result["relative_path"],
            "extension": file_path.suffix,
        }

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        numbered_content = "\n".join(
            f"{line_no}: {line}"
            for line_no, line in enumerate(lines, start=1)
        )

        return {
            "success": True,
            "path": result["relative_path"],
            "match_type": result.get("match_type"),
            "extension": file_path.suffix.lower(),
            "language": LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower(), "unknown"),
            "line_count": len(lines),
            "content": numbered_content[:max_chars],
            "truncated": len(numbered_content) > max_chars,
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "READ_ERROR",
            "error": str(e),
            "path": result["relative_path"],
        }


def read_active_file(max_chars: int = 30000) -> Dict[str, Any]:
    active_file = WORKSPACE_STATE.get("active_file")

    if not active_file:
        return {
            "success": False,
            "error_code": "NO_ACTIVE_FILE",
            "error": "No active file is currently open.",
        }

    return read_file(active_file, max_chars=max_chars)


def read_folder(path: str = ".", max_files: int = 30, max_chars_per_file: int = 8000) -> Dict[str, Any]:
    resolved = resolve_project_path(path)

    if not resolved.get("success"):
        return resolved

    base_path: Path = resolved["path"]

    if base_path.is_file():
        return {
            "success": False,
            "error_code": "NOT_A_FOLDER",
            "error": "The given path is a file, not a folder.",
            "path": resolved["relative_path"],
        }

    files_data = []
    total_files_seen = 0

    for file_path in base_path.rglob("*"):
        if is_excluded(file_path):
            continue

        if not file_path.is_file():
            continue

        if not is_text_file(file_path):
            continue

        total_files_seen += 1

        if len(files_data) >= max_files:
            continue

        relative_path = relative_to_workspace(file_path)

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")

            files_data.append(
                {
                    "path": relative_path,
                    "extension": file_path.suffix.lower(),
                    "language": LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower(), "unknown"),
                    "line_count": len(content.splitlines()),
                    "content": content[:max_chars_per_file],
                    "truncated": len(content) > max_chars_per_file,
                }
            )

        except Exception as e:
            files_data.append(
                {
                    "path": relative_path,
                    "error": str(e),
                }
            )

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "base_path": resolved["relative_path"],
        "total_text_files_seen": total_files_seen,
        "returned_file_count": len(files_data),
        "files": files_data,
        "truncated": total_files_seen > max_files,
    }


def get_file_info(path: str = "") -> Dict[str, Any]:
    result = find_file_recursively(path)

    if not result.get("success"):
        return result

    file_path: Path = result["path"]

    try:
        content = ""

        if is_text_file(file_path):
            content = file_path.read_text(encoding="utf-8", errors="replace")

        return {
            "success": True,
            "path": result["relative_path"],
            "extension": file_path.suffix.lower(),
            "language": LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower(), "unknown"),
            "size_bytes": file_path.stat().st_size,
            "length_chars": len(content),
            "line_count": len(content.splitlines()) if content else None,
            "is_text_file": is_text_file(file_path),
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "FILE_INFO_ERROR",
            "error": str(e),
            "path": result["relative_path"],
        }


def search_text(query: str, path: str = ".", max_matches: int = 100) -> Dict[str, Any]:
    query_clean = str(query or "").strip().lower()

    if not query_clean:
        return {
            "success": False,
            "error_code": "EMPTY_QUERY",
            "error": "Search query is empty.",
            "matches": [],
        }

    resolved = resolve_project_path(path)

    if not resolved.get("success"):
        return resolved

    base_path: Path = resolved["path"]
    search_paths = [base_path] if base_path.is_file() else list(base_path.rglob("*"))

    matches: List[Dict[str, Any]] = []

    for file_path in search_paths:
        if is_excluded(file_path):
            continue

        if not file_path.is_file():
            continue

        if not is_text_file(file_path):
            continue

        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_no, line in enumerate(lines, start=1):
            if query_clean in line.lower():
                matches.append(
                    {
                        "path": relative_to_workspace(file_path),
                        "line": line_no,
                        "text": line.strip(),
                    }
                )

                if len(matches) >= max_matches:
                    return {
                        "success": True,
                        "query": query,
                        "workspace_root": str(workspace_root()),
                        "base_path": resolved["relative_path"],
                        "match_count": len(matches),
                        "matches": matches,
                        "truncated": True,
                    }

    return {
        "success": True,
        "query": query,
        "workspace_root": str(workspace_root()),
        "base_path": resolved["relative_path"],
        "match_count": len(matches),
        "matches": matches,
        "truncated": False,
    }


def summarize_folder(path: str = ".") -> Dict[str, Any]:
    result = list_code_files(path)

    if not result.get("success"):
        return result

    by_language: Dict[str, int] = {}
    by_extension: Dict[str, int] = {}

    for file in result["files"]:
        language = file["language"]
        extension = file["extension"]

        by_language[language] = by_language.get(language, 0) + 1
        by_extension[extension] = by_extension.get(extension, 0) + 1

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "base_path": result["base_path"],
        "code_file_count": result["file_count"],
        "by_language": by_language,
        "by_extension": by_extension,
        "sample_files": result["files"][:50],
    }


def detect_project_type(path: str = ".") -> Dict[str, Any]:
    resolved = resolve_project_path(path)

    if not resolved.get("success"):
        return resolved

    base_path: Path = resolved["path"]

    if base_path.is_file():
        base_path = base_path.parent

    indicators = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
        "node": ["package.json"],
        "typescript": ["tsconfig.json"],
        "react": ["vite.config.js", "vite.config.ts", "next.config.js", "next.config.ts"],
        "angular": ["angular.json"],
        "dotnet": ["*.csproj", "*.sln"],
        "java_maven": ["pom.xml"],
        "java_gradle": ["build.gradle", "build.gradle.kts"],
        "php": ["composer.json"],
        "go": ["go.mod"],
        "rust": ["Cargo.toml"],
    }

    detected = []

    for project_type, patterns in indicators.items():
        for pattern in patterns:
            if "*" in pattern:
                if list(base_path.glob(pattern)):
                    detected.append(project_type)
                    break
            else:
                if (base_path / pattern).exists():
                    detected.append(project_type)
                    break

    return {
        "success": True,
        "workspace_root": str(workspace_root()),
        "base_path": relative_to_workspace(base_path) if base_path != workspace_root() else ".",
        "detected_project_types": detected or ["unknown"],
    }


def run_command(command: List[str], timeout: int = 60) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            cwd=workspace_root(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        status = "completed_successfully" if proc.returncode == 0 else "failed"

        return {
            "success": proc.returncode == 0,
            "status": status,
            "command": " ".join(command),
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-10000:],
            "stderr": proc.stderr[-10000:],
            "ran": True,
            "completed": proc.returncode == 0,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "status": "timeout",
            "command": " ".join(command),
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "ran": True,
            "completed": False,
            "error_code": "TIMEOUT",
            "error": f"Command timed out after {timeout} seconds.",
        }

    except Exception as e:
        return {
            "success": False,
            "status": "command_error",
            "command": " ".join(command),
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "ran": False,
            "completed": False,
            "error_code": "COMMAND_ERROR",
            "error": str(e),
        }


def backup_file(file_path: Path) -> Dict[str, Any]:
    """
    Create a backup of a file before editing.
    Backup format:
    filename.ext.bak
    """

    if not file_path.exists():
        return {
            "success": False,
            "error_code": "FILE_NOT_FOUND",
            "error": "Cannot backup because file does not exist.",
            "path": str(file_path),
        }

    if not file_path.is_file():
        return {
            "success": False,
            "error_code": "NOT_A_FILE",
            "error": "Cannot backup because path is not a file.",
            "path": str(file_path),
        }

    try:
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        original_content = file_path.read_text(encoding="utf-8", errors="replace")
        backup_path.write_text(original_content, encoding="utf-8")

        return {
            "success": True,
            "backup_path": relative_to_workspace(backup_path),
            "message": "Backup created successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "BACKUP_ERROR",
            "error": str(e),
            "path": relative_to_workspace(file_path),
        }


def create_file(path: str, content: str = "") -> Dict[str, Any]:
    """
    Create a new text/code file inside the current workspace.
    Does not overwrite existing files.
    """
    requested = normalize_path(path)
    if not requested:
        return {
            "success": False,
            "error_code": "MISSING_PATH",
            "error": "File path is required.",
        }

    file_path = (workspace_root() / requested).resolve()
    if not is_safe_path(file_path):
        return {
            "success": False,
            "error_code": "UNSAFE_PATH",
            "error": "Path escapes workspace root.",
            "path": requested,
        }

    if file_path.exists():
        return {
            "success": False,
            "error_code": "FILE_ALREADY_EXISTS",
            "error": "File already exists. Use update_file or replace_text instead.",
            "path": requested,
        }

    if not is_text_file(file_path):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_FILE_TYPE",
            "error": "Only text/code files can be created.",
            "path": requested,
            "extension": file_path.suffix,
        }

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        relative_path = relative_to_workspace(file_path)
        WORKSPACE_STATE["active_file"] = relative_path
        WORKSPACE_STATE["active_folder"] = normalize_path(Path(relative_path).parent)

        return {
            "success": True,
            "path": relative_path,
            "active_file": WORKSPACE_STATE["active_file"],
            "active_folder": WORKSPACE_STATE["active_folder"],
            "message": "File created successfully and set as active file.",
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "CREATE_FILE_ERROR",
            "error": str(e),
            "path": requested,
        }


def update_file(path: str = "", content: str = "") -> Dict[str, Any]:
    """
    Overwrite an existing text/code file safely.
    Creates a backup before overwriting.
    If path is empty, updates the active file.
    """

    file_result = find_file_recursively(path)
    if not file_result.get("success"):
        return file_result

    file_path: Path = file_result["path"]
    if not is_text_file(file_path):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_FILE_TYPE",
            "error": "Only text/code files can be updated.",
            "path": file_result["relative_path"],
            "extension": file_path.suffix,
        }

    backup_result = backup_file(file_path)
    if not backup_result.get("success"):
        return backup_result

    try:
        file_path.write_text(content, encoding="utf-8")
        WORKSPACE_STATE["active_file"] = file_result["relative_path"]
        WORKSPACE_STATE["active_folder"] = normalize_path(Path(file_result["relative_path"]).parent)
        return {
            "success": True,
            "path": file_result["relative_path"],
            "backup_path": backup_result["backup_path"],
            "active_file": WORKSPACE_STATE["active_file"],
            "active_folder": WORKSPACE_STATE["active_folder"],
            "message": "File updated successfully. Backup created before update.",
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "UPDATE_FILE_ERROR",
            "error": str(e),
            "path": file_result["relative_path"],
            "backup_path": backup_result.get("backup_path"),
        }


def replace_text(path: str = "", old_text: str = "", new_text: str = "") -> Dict[str, Any]:
    """
    Replace exact text inside a text/code file.
    Safer than overwriting the whole file.
    If path is empty, edits the active file.
    """

    if not old_text:
        return {
            "success": False,
            "error_code": "MISSING_OLD_TEXT",
            "error": "old_text is required for replacement.",
        }
    
    file_result = find_file_recursively(path)
    if not file_result.get("success"):
        return file_result
    
    file_path: Path = file_result["path"]
    if not is_text_file(file_path):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_FILE_TYPE",
            "error": "Only text/code files can be edited.",
            "path": file_result["relative_path"],
            "extension": file_path.suffix,
        }

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if old_text not in content:
            return {
                "success": False,
                "error_code": "TEXT_NOT_FOUND",
                "error": "The exact old_text was not found in the file.",
                "path": file_result["relative_path"],
            }

        backup_result = backup_file(file_path)
        if not backup_result.get("success"):
            return backup_result

        updated_content = content.replace(old_text, new_text, 1)
        file_path.write_text(updated_content, encoding="utf-8")
        WORKSPACE_STATE["active_file"] = file_result["relative_path"]
        WORKSPACE_STATE["active_folder"] = normalize_path(Path(file_result["relative_path"]).parent)

        return {
            "success": True,
            "path": file_result["relative_path"],
            "backup_path": backup_result["backup_path"],
            "active_file": WORKSPACE_STATE["active_file"],
            "active_folder": WORKSPACE_STATE["active_folder"],
            "message": "Text replaced successfully. Backup created before edit.",
        }

    except Exception as e:
        return {
            "success": False,
            "error_code": "REPLACE_TEXT_ERROR",
            "error": str(e),
            "path": file_result["relative_path"],
        }

def command_exists(command: str) -> bool:
    result = subprocess.run(
        ["where", command] if sys.platform.startswith("win") else ["which", command],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_file(path: str = "") -> Dict[str, Any]:
    """
    Run the active file or a given file using a safe language-specific command.
    """

    file_result = find_file_recursively(path)

    if not file_result.get("success"):
        return file_result

    file_path: Path = file_result["path"]
    relative_path = file_result["relative_path"]
    extension = file_path.suffix.lower()

    if extension == ".py":
        return {
            **run_command([sys.executable, relative_path], timeout=60),
            "tool": "run_file",
            "target_path": relative_path,
            "language": "python",
        }

    if extension in {".js", ".jsx", ".mjs", ".cjs"}:
        return {
            **run_command(["node", relative_path], timeout=60),
            "tool": "run_file",
            "target_path": relative_path,
            "language": "javascript",
        }

    if extension == ".ts":
        if command_exists("tsx"):
            return {
                **run_command(["tsx", relative_path], timeout=60),
                "tool": "run_file",
                "target_path": relative_path,
                "language": "typescript",
                "runner": "tsx",
            }

        if command_exists("ts-node"):
            return {
                **run_command(["ts-node", relative_path], timeout=60),
                "tool": "run_file",
                "target_path": relative_path,
                "language": "typescript",
                "runner": "ts-node",
            }

        return {
            "success": False,
            "error_code": "UNSUPPORTED_DIRECT_RUN",
            "error": "TypeScript files need tsx, ts-node, or project build tooling. Use run_project_tests/build later.",
            "target_path": relative_path,
            "language": "typescript",
        }

    if extension == ".tsx":
        if command_exists("tsx"):
            return {
                **run_command(["tsx", relative_path], timeout=60),
                "tool": "run_file",
                "target_path": relative_path,
                "language": "typescript_react",
                "runner": "tsx",
            }

        return {
            "success": False,
            "error_code": "UNSUPPORTED_DIRECT_RUN",
            "error": "TSX files need tsx or project build tooling. Use run_project_tests/build later.",
            "target_path": relative_path,
            "language": "typescript_react",
        }

    if extension == ".php":
        return {
            **run_command(["php", relative_path], timeout=60),
            "tool": "run_file",
            "target_path": relative_path,
            "language": "php",
        }

    if extension == ".java":
        return {
            "success": False,
            "error_code": "UNSUPPORTED_DIRECT_RUN",
            "error": "Java files usually need javac/java with classpath or Maven/Gradle project commands.",
            "target_path": relative_path,
            "language": "java",
        }

    if extension == ".cs":
        return {
            "success": False,
            "error_code": "UNSUPPORTED_DIRECT_RUN",
            "error": "C# files should usually be run through dotnet project commands.",
            "target_path": relative_path,
            "language": "csharp",
        }

    return {
        "success": False,
        "error_code": "UNSUPPORTED_FILE_RUN",
        "error": f"No safe direct runner configured for extension: {extension}",
        "target_path": relative_path,
        "extension": extension,
    }


def run_project_tests(path: str = ".") -> Dict[str, Any]:
    """
    Detect the project type and run known safe test commands.
    """

    project_result = detect_project_type(path)

    if not project_result.get("success"):
        return project_result

    detected = project_result.get("detected_project_types", [])
    root = workspace_root()

    if "python" in detected:
        return {
            **run_command([sys.executable, "-m", "pytest", "-v"], timeout=120),
            "tool": "run_project_tests",
            "project_type": "python",
        }

    if "node" in detected or "typescript" in detected or "react" in detected or "angular" in detected:
        package_json = root / "package.json"

        if package_json.exists():
            return {
                **run_command(["npm", "test"], timeout=120),
                "tool": "run_project_tests",
                "project_type": "node",
            }

        return {
            "success": False,
            "error_code": "PACKAGE_JSON_NOT_FOUND",
            "error": "Node project detected but package.json was not found at workspace root.",
        }

    if "dotnet" in detected:
        return {
            **run_command(["dotnet", "test"], timeout=180),
            "tool": "run_project_tests",
            "project_type": "dotnet",
        }

    if "java_maven" in detected:
        return {
            **run_command(["mvn", "test"], timeout=180),
            "tool": "run_project_tests",
            "project_type": "java_maven",
        }

    if "java_gradle" in detected:
        gradle_cmd = "gradlew.bat" if sys.platform.startswith("win") else "./gradlew"

        if (root / gradle_cmd).exists():
            return {
                **run_command([gradle_cmd, "test"], timeout=180),
                "tool": "run_project_tests",
                "project_type": "java_gradle",
            }

        return {
            **run_command(["gradle", "test"], timeout=180),
            "tool": "run_project_tests",
            "project_type": "java_gradle",
        }

    if "php" in detected:
        if (root / "artisan").exists():
            return {
                **run_command(["php", "artisan", "test"], timeout=180),
                "tool": "run_project_tests",
                "project_type": "php_laravel",
            }

        return {
            **run_command(["vendor/bin/phpunit"], timeout=180),
            "tool": "run_project_tests",
            "project_type": "php",
        }

    if "go" in detected:
        return {
            **run_command(["go", "test", "./..."], timeout=180),
            "tool": "run_project_tests",
            "project_type": "go",
        }

    if "rust" in detected:
        return {
            **run_command(["cargo", "test"], timeout=180),
            "tool": "run_project_tests",
            "project_type": "rust",
        }

    return {
        "success": False,
        "error_code": "UNKNOWN_PROJECT_TYPE",
        "error": "No supported project test command found.",
        "detected_project_types": detected,
    }


def run_project_build(path: str = ".") -> Dict[str, Any]:
    """
    Detect the project type and run known safe build/check commands.
    """

    project_result = detect_project_type(path)

    if not project_result.get("success"):
        return project_result

    detected = project_result.get("detected_project_types", [])
    root = workspace_root()

    if "python" in detected:
        return {
            **run_command([sys.executable, "-m", "compileall", "."], timeout=120),
            "tool": "run_project_build",
            "project_type": "python",
        }

    if "node" in detected or "typescript" in detected or "react" in detected or "angular" in detected:
        package_json = root / "package.json"

        if not package_json.exists():
            return {
                "success": False,
                "error_code": "PACKAGE_JSON_NOT_FOUND",
                "error": "package.json not found at workspace root.",
            }

        return {
            **run_command(["npm", "run", "build"], timeout=180),
            "tool": "run_project_build",
            "project_type": "node",
        }

    if "dotnet" in detected:
        return {
            **run_command(["dotnet", "build"], timeout=180),
            "tool": "run_project_build",
            "project_type": "dotnet",
        }

    if "java_maven" in detected:
        return {
            **run_command(["mvn", "compile"], timeout=180),
            "tool": "run_project_build",
            "project_type": "java_maven",
        }

    if "java_gradle" in detected:
        gradle_cmd = "gradlew.bat" if sys.platform.startswith("win") else "./gradlew"

        if (root / gradle_cmd).exists():
            return {
                **run_command([gradle_cmd, "build"], timeout=180),
                "tool": "run_project_build",
                "project_type": "java_gradle",
            }

        return {
            **run_command(["gradle", "build"], timeout=180),
            "tool": "run_project_build",
            "project_type": "java_gradle",
        }

    if "go" in detected:
        return {
            **run_command(["go", "build", "./..."], timeout=180),
            "tool": "run_project_build",
            "project_type": "go",
        }

    if "rust" in detected:
        return {
            **run_command(["cargo", "build"], timeout=180),
            "tool": "run_project_build",
            "project_type": "rust",
        }

    return {
        "success": False,
        "error_code": "UNKNOWN_PROJECT_TYPE",
        "error": "No supported project build command found.",
        "detected_project_types": detected,
    }


def run_static_analysis(path: str = ".") -> Dict[str, Any]:
    """
    Run safe static/code checks based on detected project type.
    This is not exhaustive bug detection; it returns tool output only.
    """
    project_result = detect_project_type(path)
    if not project_result.get("success"):
        return project_result

    detected = project_result.get("detected_project_types", [])
    results: Dict[str, Any] = {
        "success": True,
        "tool": "run_static_analysis",
        "detected_project_types": detected,
        "checks": {},
    }
    if "python" in detected:
        results["checks"]["compileall"] = run_command([sys.executable, "-m", "compileall", "."], timeout=120)
        if command_exists("ruff"):
            results["checks"]["ruff"] = run_command(["ruff", "check", "."], timeout=120)
        if command_exists("bandit"):
            results["checks"]["bandit"] = run_command(["bandit", "-r", "."], timeout=120)
    if "node" in detected or "typescript" in detected or "react" in detected or "angular" in detected:
        if (workspace_root() / "package.json").exists():
            results["checks"]["npm_lint"] = run_command(["npm", "run", "lint"], timeout=120)
            results["checks"]["npm_build"] = run_command(["npm", "run", "build"], timeout=180)
    if "dotnet" in detected:
        results["checks"]["dotnet_build"] = run_command(["dotnet", "build"], timeout=180)
    if "java_maven" in detected:
        results["checks"]["mvn_compile"] = run_command(["mvn", "compile"], timeout=180)
    if "go" in detected:
        results["checks"]["go_test"] = run_command(["go", "test", "./..."], timeout=180)
    if "rust" in detected:
        results["checks"]["cargo_check"] = run_command(["cargo", "check"], timeout=180)
    if not results["checks"]:
        return {
            "success": False,
            "error_code": "NO_STATIC_ANALYSIS_AVAILABLE",
            "error": "No static analysis command is configured for this project type.",
            "detected_project_types": detected,
        }
    results["success"] = all(check.get("success") is True for check in results["checks"].values())
    return results

