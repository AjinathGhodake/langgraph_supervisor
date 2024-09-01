# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
from constants import OPTIONS


# Using openai function calling can make output parsing easier for us
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": OPTIONS},
                ],
            }
        },
        "required": ["next"],
    },
}

json_schema = {
    "name": "format_json_schema",
    "description": "Formats a Python dictionary as a JSON schema string.",
    "parameters": {
        "type": "object",
        "properties": {
            "schema": {
                "type": "object",
                "description": "The Python dictionary representing the JSON schema.",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                    "is_student": {"type": "boolean"},
                    "courses": {"type": "array", "items": {"type": "string"}},
                },
            }
        },
        "required": ["schema"],
    },
}
