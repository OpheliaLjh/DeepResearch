from typing import Any, Dict, Callable
from tools.web_search import web_search_impl

# Map tool names → implementation functions
TOOL_MAP: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "web_search": web_search_impl,
}

def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch function calls from the OpenAI Responses API
    to the corresponding local tool implementations.
    """
    func = TOOL_MAP.get(name)
    if func is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(args)
    except Exception as e:
        return {"error": str(e), "tool": name}
