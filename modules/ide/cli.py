import json
from typing import Any, Dict, List

from core.logger_config import setup_logger
from modules.ide.agent import execute_ide_agent
from modules.ide.tools import (
    ROOT_DIR,
    get_workspace_context,
    run_file,
    select_file_dialog,
    select_workspace_folder,
)
from modules.github.tools import (
    git_current_branch,
    git_diff,
    git_status,
    git_commit,
    git_add_all,
    git_create_branch
)

logger = setup_logger()


def print_json(title: str, data: Dict[str, Any]) -> None:
    print(f"\n{title}:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")


def run_ide_cli() -> None:
    print("[IDE_CLI] Version 2 Phase 5 IDE Assistant")
    print(f"[IDE_CLI] Default workspace root: {ROOT_DIR}")
    print("Type 'exit' to quit.")
    print("Type 'reset' to clear chat memory.")
    print("Type '/open-file' to open file dialog.")
    print("Type '/open-folder' to open folder dialog.")
    print("Type '/context' to view active workspace/file/folder.")
    print("Type '/run-file' to run the active file and show raw output.")
    print("Type '/fix-run' to run, debug, safely fix, and run again.")
    print("Type '/git-status' to show changed files.")
    print("Type '/git-diff' to show current code diff.")
    print("Type '/git-branch' to show current Git branch.")
    print("Type '/git-stage' to stage all current changes.")
    print("Type '/git-commit' to commit staged changes.")
    print("Type '/git-create-branch' to create and switch to a new branch.")
    print("")
    print("")

    chat_history: List[Dict[str, Any]] = []

    while True:
        user_question = input("IDE Agent: ").strip()

        if user_question.lower() in {"exit", "quit"}:
            break

        if user_question.lower() == "reset":
            chat_history = []
            print("[IDE_CLI] Chat memory reset.\n")
            continue

        if user_question.lower() in {"/open-file", "open file dialog", "select file"}:
            result = select_file_dialog()
            print_json("[IDE_CLI] File dialog result", result)
            continue

        if user_question.lower() in {"/open-folder", "open folder dialog", "select workspace folder"}:
            result = select_workspace_folder()
            print_json("[IDE_CLI] Folder dialog result", result)
            continue

        if user_question.lower() == "/context":
            result = get_workspace_context()
            print_json("[IDE_CLI] Workspace context", result)
            continue

        if user_question.lower() in {"/run-file", "/run-active", "run active file"}:
            result = run_file("")
            print_json("[IDE_CLI] Raw run result", result)
            continue

        if user_question.lower() in {"/fix-run", "/debug-run", "/auto-fix"}:
            answer, chat_history = execute_ide_agent(
                user_question=(
                    "Run the active file. If it fails, inspect the error, "
                    "read the active file, apply the smallest safe fix with backup, "
                    "run it again, and report before/after status."
                ),
                chat_history=chat_history,
            )

            print(f"\nAgent:\n{answer}\n")
            continue
        if user_question.lower() in {"/git-status", "git status"}:
            result = git_status()
            print_json("[IDE_CLI] Git status", result)
            continue

        if user_question.lower() in {"/git-diff", "git diff"}:
            result = git_diff()
            print_json("[IDE_CLI] Git diff", result)
            continue

        if user_question.lower() in {"/git-branch", "git branch"}:
            result = git_current_branch()
            print_json("[IDE_CLI] Current Git branch", result)
            continue

        if user_question.lower() in {"/git-stage", "git stage", "git add"}:
            confirm = input(
                "This will run 'git add .' and stage all changes. Continue? (yes/no): "
            ).strip().lower()

            if confirm != "yes":
                print("[IDE_CLI] Git stage cancelled.\n")
                continue

            result = git_add_all()
            print_json("[IDE_CLI] Git stage result", result)
            continue

        if user_question.lower() in {"/git-commit", "git commit"}:
            message = input("Enter commit message: ").strip()
            if not message:
                print("[IDE_CLI] Commit cancelled. Commit message is required.\n")
                continue
            confirm = input(
                f"This will run git commit -m \"{message}\". Continue? (yes/no): "
            ).strip().lower()
            if confirm != "yes":
                print("[IDE_CLI] Git commit cancelled.\n")
                continue
            result = git_commit(message)
            print_json("[IDE_CLI] Git commit result", result)
            continue

        if user_question.lower() in {"/git-create-branch", "git create branch", "git new branch"}:
            branch_name = input("Enter new branch name: ").strip()

            if not branch_name:
                print("[IDE_CLI] Branch creation cancelled. Branch name is required.\n")
                continue

            confirm = input(
                f"This will run git checkout -b \"{branch_name}\". Continue? (yes/no): "
            ).strip().lower()

            if confirm != "yes":
                print("[IDE_CLI] Git branch creation cancelled.\n")
                continue

            result = git_create_branch(branch_name)
            print_json("[IDE_CLI] Git create branch result", result)
            continue

        if not user_question:
            continue

        answer, chat_history = execute_ide_agent(
            user_question=user_question,
            chat_history=chat_history,
        )

        print(f"\nAgent:\n{answer}\n")