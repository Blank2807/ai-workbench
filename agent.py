import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from logger_config import setup_logger
from tools import (
    ROOT_DIR,
    clear_active_context,
    create_file,
    detect_language_by_path,
    detect_project_type,
    get_file_info,
    get_workspace_context,
    list_code_files,
    list_files,
    open_file,
    open_folder,
    read_active_file,
    read_file,
    read_folder,
    replace_text,
    run_file,
    run_project_build,
    run_project_tests,
    run_static_analysis,
    search_text,
    select_file_dialog,
    select_workspace_folder,
    set_workspace,
    summarize_folder,
    update_file,
)


load_dotenv()
logger = setup_logger()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"


TOOLS = [
    {
        "type": "function",
        "name": "get_workspace_context",
        "description": "Get current workspace root, active file, and active folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "set_workspace",
        "description": "Set/open a workspace folder using an explicit folder path.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative folder path to use as workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "select_workspace_folder",
        "description": "Open a folder picker dialog and set the selected folder as the workspace.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "open_file",
        "description": "Open a file and set it as the active file. This does not visually open an editor; it sets IDE context.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path or filename, for example tools.py, src/app.tsx, Program.cs.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "open_folder",
        "description": "Open a folder inside the current workspace and set it as the active folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative folder path inside the workspace. Use '.' for workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "clear_active_context",
        "description": "Clear active file and active folder context.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_files",
        "description": "List all files inside the workspace, active folder, or a specific folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to list. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_code_files",
        "description": "List supported code/text files with detected language information.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to scan. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a code/text file. Supports exact relative paths and filename-only recursive lookup.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path or filename. If empty, use active file.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return from the file.",
                },
            },
            "required": ["path", "max_chars"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_active_file",
        "description": "Read the currently active file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return from the active file.",
                }
            },
            "required": ["max_chars"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_folder",
        "description": "Read multiple code/text files from a folder with limits. Useful for folder-level understanding.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to read. Use '.' for active folder/workspace root.",
                },
                "max_files": {
                    "type": "integer",
                    "description": "Maximum number of files to read.",
                },
                "max_chars_per_file": {
                    "type": "integer",
                    "description": "Maximum characters to read per file.",
                },
            },
            "required": ["path", "max_files", "max_chars_per_file"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_text",
        "description": "Search for text across the workspace, active folder, or a specific folder/file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for, for example auth, login, database, function name, class name, API route.",
                },
                "path": {
                    "type": "string",
                    "description": "Folder/file path to search in. Use '.' for active folder/workspace root.",
                },
                "max_matches": {
                    "type": "integer",
                    "description": "Maximum number of matches to return.",
                },
            },
            "required": ["query", "path", "max_matches"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_file_info",
        "description": "Return metadata for a file such as extension, language, size, and line count. If path is empty, use active file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path, filename, or empty string for active file.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "summarize_folder",
        "description": "Summarize a folder by language, extension, and sample files.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to summarize. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detect_language_by_path",
        "description": "Detect programming language based on a file path or extension.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path, for example app.py, index.tsx, Program.cs, or query.sql.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detect_project_type",
        "description": "Detect project type based on common project files like package.json, requirements.txt, pom.xml, .csproj, composer.json, go.mod, etc.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Project/folder path. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "create_file",
    "description": "Create a new text/code file inside the workspace. Does not overwrite existing files.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path to create, for example src/utils.py.",
            },
            "content": {
                "type": "string",
                "description": "Full initial file content.",
            },
        },
        "required": ["path", "content"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "update_file",
    "description": "Overwrite an existing text/code file. Creates a backup before updating. Empty path means active file.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            },
            "content": {
                "type": "string",
                "description": "Full replacement file content.",
            },
        },
        "required": ["path", "content"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "replace_text",
    "description": "Replace exact text inside an existing text/code file. Creates a backup before editing. Empty path means active file.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            },
            "old_text": {
                "type": "string",
                "description": "Exact text to replace.",
            },
            "new_text": {
                "type": "string",
                "description": "Replacement text.",
            },
        },
        "required": ["path", "old_text", "new_text"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "run_file",
    "description": "Run the active file or a given file using safe language-specific execution. Supports direct run for Python, JavaScript, and PHP files.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
},
{
    "type": "function",
    "name": "run_project_tests",
    "description": "Detect project type and run known safe test command, such as pytest, npm test, dotnet test, mvn test, go test, or cargo test.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    },
    {
    "type": "function",
    "name": "run_project_build",
    "description": "Detect project type and run known safe build/check command, such as compileall, npm run build, dotnet build, mvn compile, go build, or cargo build.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "run_static_analysis",
    "description": "Run safe static/code checks based on detected project type. Examples: compileall, ruff, bandit, npm lint/build, dotnet build, mvn compile.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
},
]


BASE_INSTRUCTIONS = """
You are a Multi-language IDE code assistant with an error auto-fix loop.

Your current job is:
- manage workspace context
- open/select active files and folders
- inspect files
- inspect folders
- detect languages
- detect project type
- search code
- read code
- explain code
- answer questions from the code with evidence
- create_file(path, content)
- update_file(path, content)
- replace_text(path, old_text, new_text)
- run code, inspect errors, safely fix code, and run again
- explain whether the fix worked based on the second run result

You are allowed to inspect, edit safely, run files, run tests, build projects, and perform static analysis.
You are NOT generating PDF/DOCX documents yet.

Available tools:
- get_workspace_context()
- set_workspace(path)
- select_workspace_folder()
- open_file(path)
- open_folder(path)
- clear_active_context()
- list_files(path)
- list_code_files(path)
- read_file(path, max_chars)
- read_active_file(max_chars)
- read_folder(path, max_files, max_chars_per_file)
- search_text(query, path, max_matches)
- get_file_info(path)
- summarize_folder(path)
- detect_language_by_path(path)
- detect_project_type(path)
- run_file(path)
- run_project_tests(path)
- run_project_build(path)
- run_static_analysis(path)

Behavior rules:
1. Always use tools before answering questions about the codebase.
2. Use the minimum number of tools needed.
3. Treat "open file" as setting active file context.
4. Treat "open folder" as setting active folder context.
5. Treat "open project/workspace" as setting workspace root.
6. If the user says "this file", "current file", "active file", or "selected file", use read_active_file().
7. If the user says "this folder", "current folder", or "active folder", use path "." because "." resolves to active folder.
8. For "what is currently open", use get_workspace_context().
9. For "what files are there", use list_files(".") or list_code_files(".").
10. For "explain this file", use read_active_file(30000).
11. For "explain <filename>", use open_file(filename), then read_active_file(30000).
12. For "explain this folder/project", use summarize_folder(".") first, then read_folder(".", 20, 6000) if needed.
13. For "where is X implemented", use search_text(query, ".", 100), then read the most relevant files if needed.
14. For "what language/project is this", use detect_project_type(".") and summarize_folder(".").
15. If a file is too large or truncated, say that it was truncated and ask for a narrower target if needed.
16. Always mention relevant file paths as evidence.
17. Mention line numbers when tool results provide line numbers.
18. If multiple files match a filename, ask the user to choose from possible_matches.
19. If the user asks to test, edit, create files, generate PDF/DOCX, or run commands, say that this is planned for later phases and explain what Phase 2 can do now.
20. Keep answers practical and concise.
21. For creating a new file, use create_file(path, content).
22. For small edits, prefer replace_text(path, old_text, new_text).
23. For full-file rewrites, use update_file(path, content).
24. Before editing, read the target file unless the user provided exact old_text and target path.
25. Never edit a file if the target is ambiguous.
26. After editing, mention the changed file path and backup path returned by the tool.
27. If replace_text returns TEXT_NOT_FOUND, do not guess. Ask the user for the exact text or read the file and propose a safer replacement.
28. If the user asks to fix code, first read the relevant file, then use replace_text or update_file.
29. If the user asks to run this file or execute active file, use run_file("").
30. If the user asks to run a specific file, use run_file(path).
31. If the user asks to run tests, use run_project_tests(".").
32. If the user asks to build/check the project, use run_project_build(".").
33. If the user asks to check bugs, code quality, lint, security, or static issues, use run_static_analysis(".").
34. Do not run arbitrary shell commands. Only use the safe execution tools exposed.
35. After running a command tool, summarize command, exit code, stdout, stderr, and likely next action.
36. If tests/build/static analysis fail, do not claim the code is broken until you explain the specific tool output.
37. If no supported test/build/analyze command is found, explain the detected project type and what command support is missing.
38. If the user asks "check code and tell bugs", use run_static_analysis(".") first, then read relevant files if needed.
39. If the user asks "test this file", explain that file-level testing depends on language/project; use run_file("") for executable scripts or run_project_tests(".") for project tests.
40. When using run_file, run_project_tests, run_project_build, or run_static_analysis, always report:
- command
- success true/false
- exit_code
- stdout summary
- stderr/error summary
- final conclusion: completed successfully, failed, or partially ran then crashed.
41. If stderr contains a traceback, say the code started but crashed; do not say only "ran successfully".
42. If success is false, explain the exact failure reason from stderr/error.
43. If the user asks "fix and run", "fix this code", "solve this error", "debug this file", or similar, follow this loop:
    a. Run the active file using run_file("").
    b. If it succeeds, report that no runtime error was found.
    c. If it fails, inspect stderr/error/exit_code.
    d. Read the active file using read_active_file(30000).
    e. Identify the smallest safe code change.
    f. Prefer replace_text("", old_text, new_text) for small edits.
    g. Use update_file("", content) only if a larger rewrite is necessary.
    h. Run the file again using run_file("").
    i. Report before status, changed file, backup path, after status, stdout, stderr, and conclusion.
44. Never claim an error is fixed until you run the file again and the second run succeeds.
45. If the second run fails with a different error, say that the original issue may be fixed but a new error remains. Then summarize the new error.
46. If the required fix is unclear, do not edit. Explain what information is missing.
47. If stderr has a traceback, identify:
    - exception type
    - failing file
    - failing line if available
    - failing function if visible
    - probable cause
48. For UnicodeEncodeError on Windows console output, prefer changing the print/output handling safely instead of changing business logic.
49. If the code requires external credentials, browser access, network access, API keys, or user interaction, mention that the run result may depend on the local environment.
50. Keep the fix minimal. Do not refactor unrelated code during auto-fix.

Important examples:
- "Open project D:\\MyApp" -> set_workspace("D:\\MyApp")
- "Select workspace folder" -> select_workspace_folder()
- "Open tools.py" -> open_file("tools.py")
- "Open src folder" -> open_folder("src")
- "What is open?" -> get_workspace_context()
- "Explain this file" -> read_active_file(30000)
- "List files here" -> list_files(".")
- "Where is login implemented?" -> search_text("login", ".", 100), then read relevant files
- "Create utils.py with helper functions" -> create_file("utils.py", content)
- "Fix this file" -> read_active_file(30000), then replace_text("", old_text, new_text)
- "Replace X with Y in this file" -> replace_text("", "X", "Y")
- "Rewrite this file" -> read_active_file(30000), then update_file("", content)
- "Run this file" -> run_file("")
- "Run app.py" -> run_file("app.py")
- "Run tests" -> run_project_tests(".")
- "Build project" -> run_project_build(".")
- "Check bugs" -> run_static_analysis(".")
- "Check code quality" -> run_static_analysis(".")
- "Fix this code and run again" -> run_file(""), read_active_file(30000), replace_text/update_file, run_file("")
- "Solve this error" -> inspect previous run if available; otherwise run_file(""), then fix loop
- "Debug this file" -> run_file(""), inspect stderr, read_active_file(30000), fix safely, run_file("")
- "It crashed, fix it" -> run_file(""), inspect error, read_active_file(30000), edit, run again
"""


def extract_function_calls(response) -> List[Any]:
    function_calls = []

    for item in response.output:
        if item.type == "function_call":
            function_calls.append(item)

    return function_calls


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"[AGENT.PY] EXECUTING TOOL {tool_name} | args: {arguments}")

    try:
        if tool_name == "get_workspace_context":
            return get_workspace_context()

        if tool_name == "set_workspace":
            return set_workspace(arguments.get("path", ""))

        if tool_name == "select_workspace_folder":
            return select_workspace_folder()

        if tool_name == "open_file":
            return open_file(arguments.get("path", ""))

        if tool_name == "open_folder":
            return open_folder(arguments.get("path", "."))

        if tool_name == "clear_active_context":
            return clear_active_context()

        if tool_name == "list_files":
            return list_files(arguments.get("path", "."))

        if tool_name == "list_code_files":
            return list_code_files(arguments.get("path", "."))

        if tool_name == "read_file":
            return read_file(
                path=arguments.get("path", ""),
                max_chars=arguments.get("max_chars", 30000),
            )

        if tool_name == "read_active_file":
            return read_active_file(arguments.get("max_chars", 30000))

        if tool_name == "read_folder":
            return read_folder(
                path=arguments.get("path", "."),
                max_files=arguments.get("max_files", 30),
                max_chars_per_file=arguments.get("max_chars_per_file", 8000),
            )

        if tool_name == "search_text":
            return search_text(
                query=arguments.get("query", ""),
                path=arguments.get("path", "."),
                max_matches=arguments.get("max_matches", 100),
            )

        if tool_name == "get_file_info":
            return get_file_info(arguments.get("path", ""))

        if tool_name == "summarize_folder":
            return summarize_folder(arguments.get("path", "."))

        if tool_name == "detect_language_by_path":
            return detect_language_by_path(arguments.get("path", ""))

        if tool_name == "detect_project_type":
            return detect_project_type(arguments.get("path", "."))

        if tool_name == "create_file":
            return create_file(
                path=arguments.get("path", ""),
                content=arguments.get("content", ""),
            )

        if tool_name == "update_file":
            return update_file(
                path=arguments.get("path", ""),
                content=arguments.get("content", ""),
            )

        if tool_name == "replace_text":
            return replace_text(
                path=arguments.get("path", ""),
                old_text=arguments.get("old_text", ""),
                new_text=arguments.get("new_text", ""),
            )

        if tool_name == "run_file":
            return run_file(arguments.get("path", ""))

        if tool_name == "run_project_tests":
            return run_project_tests(arguments.get("path", "."))

        if tool_name == "run_project_build":
            return run_project_build(arguments.get("path", "."))

        if tool_name == "run_static_analysis":
            return run_static_analysis(arguments.get("path", "."))
        
        return {
            "success": False,
            "error_code": "UNKNOWN_TOOL",
            "error": f"Unknown tool name: {tool_name}",
        }

    except Exception as e:
        logger.exception(f"[AGENT.PY] Tool execution failed: {tool_name}")

        return {
            "success": False,
            "error_code": "TOOL_EXECUTION_ERROR",
            "tool": tool_name,
            "arguments": arguments,
            "error": str(e),
        }


def create_response(input_items, instructions: str):
    payload = {
        "model": MODEL,
        "instructions": instructions,
        "input": input_items,
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    return client.responses.create(**payload)


def response_item_to_input_item(item):
    """
    Convert Responses API output items into input items so we can preserve
    conversation and tool-call context manually without previous_response_id.
    This is needed when Zero Data Retention does not allow previous_response_id.
    """

    if item.type == "function_call":
        return {
            "type": "function_call",
            "call_id": item.call_id,
            "name": item.name,
            "arguments": item.arguments,
        }

    if item.type == "message":
        content_items = []

        for content in item.content:
            if content.type == "output_text":
                content_items.append(
                    {
                        "type": "input_text",
                        "text": content.text,
                    }
                )

        return {
            "role": "assistant",
            "content": content_items,
        }

    return None


def execute_agent(user_question: str,chat_history: List[Dict[str, Any]],) -> tuple[str, List[Dict[str, Any]]]:
    input_items = []

    input_items.extend(chat_history[-12:])

    input_items.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    current_turn_items = list(input_items)
    max_tool_call_rounds = 8

    for round_index in range(max_tool_call_rounds):
        logger.info(f"[AGENT.PY] TOOL LOOP ROUND: {round_index + 1}")

        response = create_response(
            input_items=current_turn_items,
            instructions=BASE_INSTRUCTIONS,
        )

        function_calls = extract_function_calls(response)

        for output_item in response.output:
            converted_item = response_item_to_input_item(output_item)

            if converted_item:
                current_turn_items.append(converted_item)

        if not function_calls:
            final_answer = response.output_text or ""

            chat_history.append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            chat_history.append(
                {
                    "role": "assistant",
                    "content": final_answer,
                }
            )

            return final_answer, chat_history

        for tool_call in function_calls:
            tool_name = tool_call.name

            try:
                arguments = json.loads(tool_call.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}

            tool_result = execute_tool(tool_name, arguments)

            current_turn_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(tool_result, ensure_ascii=False),
                }
            )

    final_answer = (
        "Unable to produce a final answer within the tool-call round limit. "
        "Try asking a narrower question."
    )

    return final_answer, chat_history


if __name__ == "__main__":
    print("[AGENT.PY] Version 2 Phase 4 IDE Assistant")
    print(f"[AGENT.PY] Default workspace root: {ROOT_DIR}")
    print("Type 'exit' to quit.")
    print("Type 'reset' to clear chat memory.")
    print("Type '/open-file' to open file dialog.")
    print("Type '/open-folder' to open folder dialog.")
    print("Type '/context' to view active workspace/file/folder.")
    print("Type '/run-file' to run the active file and show raw output.")
    print("Type '/fix-run' to run, debug, safely fix, and run again.")
    print("")
    print("")

    chat_history: List[Dict[str, Any]] = []

    while True:
        user_question = input("IDE Agent: ").strip()

        if user_question.lower() in {"exit", "quit"}:
            break

        if user_question.lower() == "reset":
            chat_history = []
            print("[AGENT.PY] Chat memory reset.\n")
            continue

        if user_question.lower() in {"/open-file", "open file dialog", "select file"}:
            result = select_file_dialog()
            print(f"\n[AGENT.PY] File dialog result:\n{json.dumps(result, indent=2)}\n")
            continue

        if user_question.lower() in {"/open-folder", "open folder dialog", "select workspace folder"}:
            result = select_workspace_folder()
            print(f"\n[AGENT.PY] Folder dialog result:\n{json.dumps(result, indent=2)}\n")
            continue

        if user_question.lower() == "/context":
            result = get_workspace_context()
            print(f"\n[AGENT.PY] Workspace context:\n{json.dumps(result, indent=2)}\n")
            continue

        if user_question.lower() in {"/run-file", "/run-active", "run active file"}:
            result = run_file("")
            print(f"\n[AGENT.PY] Raw run result:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
            continue

        if user_question.lower() in {"/fix-run", "/debug-run", "/auto-fix"}:
            answer, chat_history = execute_agent(
                user_question=(
                    "Run the active file. If it fails, inspect the error, "
                    "read the active file, apply the smallest safe fix with backup, "
                    "run it again, and report before/after status."
                ),
                chat_history=chat_history,
            )

            print(f"\nAgent:\n{answer}\n")
            continue
        if not user_question:
            continue

        answer, chat_history = execute_agent(
            user_question=user_question,
            chat_history=chat_history,
        )

        print(f"\nAgent:\n{answer}\n")