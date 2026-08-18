from typing import Any, Dict, List, Tuple

from core.logger_config import setup_logger
from core.response_loop import run_tool_call_loop
from modules.ide.prompts import IDE_BASE_INSTRUCTIONS
from modules.ide.tool_schemas import IDE_TOOLS
from modules.ide.tools import (
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
    select_workspace_folder,
    set_workspace,
    summarize_folder,
    update_file,
)


logger = setup_logger()


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute IDE-specific tools.

    This function is passed into the reusable core response loop.
    The core loop handles OpenAI tool calling.
    This function only maps tool names to actual Python functions.
    """

    logger.info(f"[IDE_AGENT] EXECUTING TOOL {tool_name} | args: {arguments}")

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
            return read_active_file(
                max_chars=arguments.get("max_chars", 30000)
            )

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
        logger.exception(f"[IDE_AGENT] Tool execution failed: {tool_name}")

        return {
            "success": False,
            "error_code": "TOOL_EXECUTION_ERROR",
            "tool": tool_name,
            "arguments": arguments,
            "error": str(e),
        }


def execute_ide_agent(
    user_question: str,
    chat_history: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run the IDE specialist agent.

    The reusable OpenAI Responses API loop lives in core.response_loop.
    This function only supplies:
    - IDE instructions
    - IDE tool schemas
    - IDE tool executor
    """

    return run_tool_call_loop(
        user_question=user_question,
        chat_history=chat_history,
        instructions=IDE_BASE_INSTRUCTIONS,
        tools=IDE_TOOLS,
        execute_tool=execute_tool,
        agent_name="IDE_AGENT",
        max_tool_call_rounds=8,
    )