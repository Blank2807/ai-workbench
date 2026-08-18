import json
from typing import Any, Callable, Dict, List, Tuple
from openai import OpenAI
from core.config import OPENAI_API_KEY, OPENAI_MODEL
from core.logger_config import setup_logger

logger = setup_logger()
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = OPENAI_MODEL


ToolExecutor = Callable[[str, Dict[str, Any]], Dict[str, Any]]
def extract_function_calls(response) -> List[Any]:
    """
    Extract function_call items from an OpenAI Responses API response.
    """

    function_calls = []

    for item in response.output:
        if item.type == "function_call":
            function_calls.append(item)

    return function_calls


def response_item_to_input_item(item):
    """
    Convert Responses API output items into input items so we can preserve
    conversation and tool-call context manually without previous_response_id.

    This is required for Zero Data Retention environments where
    previous_response_id may not be allowed.
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


def create_response(input_items: List[Dict[str, Any]],instructions: str,tools: List[Dict[str, Any]],):
    """
    Create a Responses API call using the supplied instructions and tools.
    """

    payload = {
        "model": MODEL,
        "instructions": instructions,
        "input": input_items,
        "tools": tools,
        "tool_choice": "auto",
    }

    return client.responses.create(**payload)


def run_tool_call_loop(user_question: str,chat_history: List[Dict[str, Any]],instructions: str,tools: List[Dict[str, Any]],execute_tool: ToolExecutor,agent_name: str = "AGENT",max_tool_call_rounds: int = 8,) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Reusable OpenAI Responses API function-calling loop.

    This function:
    - adds recent chat history
    - sends user question to the model
    - detects function calls
    - executes tools using the module-specific execute_tool callback
    - sends function_call_output back to the model
    - returns final answer and updated chat history
    """

    input_items: List[Dict[str, Any]] = []

    input_items.extend(chat_history[-12:])

    input_items.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    current_turn_items = list(input_items)

    for round_index in range(max_tool_call_rounds):
        logger.info(f"[{agent_name}] TOOL LOOP ROUND: {round_index + 1}")

        response = create_response(
            input_items=current_turn_items,
            instructions=instructions,
            tools=tools,
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