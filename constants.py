from typing import Literal

MEMBERS = [
    "Initialization",
    "Testing",
    "File_reader",
    # "Code_converter",
    "Controller_Writer",
]
OPTIONS = ["FINISH"] + MEMBERS

LLM_PLATFORM: Literal["openai", "ollama", "groq"] = "groq"
