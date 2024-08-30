import functools
from langgraph.graph import END, StateGraph, START
from src.utils.nodes import _get_model, agent_node, create_agent
from src.utils.state import AgentState
from src.utils.tools import create_spring_boot_app, tavily_tool
from src.utils.function_definition import function_def

from src.utils.prompt import supervisor_prompt
from constants import MEMBERS
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

model = _get_model("groq")

supervisor_node = (
    supervisor_prompt
    | model.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)


research_agent = create_agent("groq", "You are a web researcher.", [tavily_tool])
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
code_agent = create_agent(
    "groq",
    "You have too call create_spring_boot_app to create boilerplate code of spring boot framework",
    [create_spring_boot_app],
)
code_node = functools.partial(agent_node, agent=code_agent, name="Coder")

workflow = StateGraph(AgentState)
workflow.add_node("Researcher", research_node)
workflow.add_node("Coder", code_node)
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
            HumanMessage(content="Create spring boot application, boot version 3.3.3")
        ]
    },
    {"recursion_limit": 10},
):
    # if "__end__" not in s:
    print(s)
    print("----")

# from my_agent.agent import graph
# from langchain_core.messages import HumanMessage
# from dotenv import load_dotenv

# load_dotenv()

# events = graph.stream(
#     {
#         "messages": [HumanMessage(content="want to create spring boot application")],
#     },
#     # Maximum number of steps to take in the graph
#     {"recursion_limit": 2},
# )
# for s in events:
#     print(s)
#     print("----")
