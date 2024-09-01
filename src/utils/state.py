from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence
import operator


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    def __init__(self):
        self.data = {}
        self.messages = []

    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    # agent_scratchpad: Annotated[Sequence[BaseMessage], operator.add]
    def set_application_structure(self, structure):
        self.data["application_structure"] = structure

    def get_application_structure(self):
        return self.data.get("application_structure", None)
