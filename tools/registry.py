tools = [
    {
        "type": "function",
        "name": "web_search",
        "description": "Search the web and return results (title, url, snippet, time).",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                "recency_days": {"type": "integer", "default": 3650}
            },
            "required": ["query"]
        }
    },
    {
        "type": "function",
        "name": "http_fetch",
        "description": "Fetch a webpage or PDF. Returns base64 + content type.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    },
    {
        "type": "function",
        "name": "extract_text",
        "description": "Extract main text and links from HTML/PDF.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "content_base64": {"type": "string"},
                "content_type": {"type": "string", "enum": ["html", "pdf", "text"]},
                "url": {"type": "string"}
            },
            "required": ["content_base64", "content_type"]
        }
    },
]
