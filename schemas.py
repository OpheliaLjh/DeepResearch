planner_schema = {
    "name": "Plan",
    "schema": {
        "type": "object",
        "properties": {
            "intents": {"type": "array", "items": {"type": "string"}},
            "queries": {"type": "array", "items": {"type": "string"}},
            "targets": {"type": "array", "items": {"type": "string"}},
            "risks":   {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False,
        "required": ["intents", "queries", "targets", "risks"]
    }
}

critic_schema = {
    "name": "Critique",
    "schema": {
        "type": "object",
        "properties": {
            "sufficient": {"type": "boolean"},
            "gaps": {"type": "array", "items": {"type": "string"}},
            "next_queries": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False,
        "required": ["sufficient", "gaps", "next_queries"]
    }
}

report_schema = {
    "name": "ResearchReport",
    "schema": {
        "type": "object",
        "properties": {
            "tldr": {"type": "string"},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "bullets": {"type": "array", "items": {"type": "string"}},
                        "citations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string"},
                                    "title": {"type": "string"},
                                    "published_at": {"type": "string"},
                                    "snippet": {"type": "string"},
                                },
                                "additionalProperties": False,
                                "required": ["url", "title", "published_at", "snippet"]
                            }
                        }
                    },
                    "additionalProperties": False,
                    "required": ["title", "bullets", "citations"]
                }
            },
            "next_todos": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False,
        "required": ["tldr","sections","next_todos"]
    }
}
