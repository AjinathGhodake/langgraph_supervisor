from dotenv import load_dotenv

load_dotenv()
import functools
from langgraph.graph import END, StateGraph, START
from src.utils.nodes import _get_model, agent_node, create_agent
from src.utils.state import AgentState
from src.utils.tools import (
    initialize_spring_boot_app,
    spring_boot_code_exists_test,
    # tavily_tool,
)
from src.utils.function_definition import function_def

from src.utils.prompt import supervisor_prompt
from constants import MEMBERS
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser

from langchain_core.messages import HumanMessage


model = _get_model("groq")

supervisor_node = (
    supervisor_prompt
    | model.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)


# research_agent = create_agent("groq", "You are a web researcher.", [tavily_tool])
# research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
initialization_agent = create_agent(
    "groq",
    "You are an expert in initializing Spring Boot applications. Your task is to set up the application"
    " with the provided parameters and ensure it is generated correctly.",
    [initialize_spring_boot_app],
)
initialization_node = functools.partial(
    agent_node, agent=initialization_agent, name="initialization"
)

testing_agent = create_agent(
    "groq",
    "You are an expert in testing Spring Boot applications. Your task is to perform"
    " tests on the initialized application and ensure everything is functioning as expected.",
    [spring_boot_code_exists_test],
)
testing_node = functools.partial(agent_node, agent=testing_agent, name="testing")
workflow = StateGraph(AgentState)
# workflow.add_node("Researcher", research_node)
workflow.add_node("initialization", initialization_node)
workflow.add_node("testing", testing_node)
workflow.add_node("supervisor", supervisor_node)

for member in MEMBERS:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in MEMBERS}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.add_edge(START, "supervisor")

graph = workflow.compile()

for s in graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Initialize spring boot application, boot version 3.3.3, and write api for get hello word text"
            )
        ]
    },
    {"recursion_limit": 10},
):
    # if "__end__" not in s:
    print(s)
    print("----")
