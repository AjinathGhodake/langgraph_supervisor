from dotenv import load_dotenv

load_dotenv()
import functools
from langgraph.graph import END, StateGraph, START
from src.utils.nodes import (
    _get_model,
    agent_node,
    create_agent,
    update_application_structure,
)
from src.utils.state import AgentState
from src.utils.tools import (
    initialize_spring_boot_app,
    read_file_content,
    spring_boot_code_exists_test,
    write_controller_code,
    default_tool,
    # tavily_tool,
)
from src.utils.function_definition import function_def
from src.utils.prompt import supervisor_prompt
from constants import LLM_PLATFORM, MEMBERS
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import HumanMessage


model = _get_model(LLM_PLATFORM)

supervisor_node = (
    supervisor_prompt
    | model.bind_functions(
        functions=[function_def],
    )
    | JsonOutputFunctionsParser()
)

# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
initialization_agent = create_agent(
    LLM_PLATFORM,
    "You are an expert in initializing Spring Boot applications. Your task is to set up the application"
    " with the provided parameters and ensure it is generated correctly.",
    [initialize_spring_boot_app],
)
initialization_node = functools.partial(
    agent_node, agent=initialization_agent, name="Initialization"
)

testing_agent = create_agent(
    LLM_PLATFORM,
    "You are an expert in testing Spring Boot applications. Your task is to perform"
    " tests on the initialized application and ensure everything is functioning as expected.",
    [spring_boot_code_exists_test],
)
testing_node = functools.partial(agent_node, agent=testing_agent, name="Testing")

file_reader_agent = create_agent(
    LLM_PLATFORM,
    "You are an expert in reading and analyzing PHP code. Your task is to read the PHP file from the specified path and extract its entire content as text."
    " The extracted code will then be used for transformation or migration to a different language or framework."
    " Please ensure that the content is read accurately, preserving all code details, comments, and structure.",
    [read_file_content],
)
file_reader_node = functools.partial(
    agent_node, agent=file_reader_agent, name="File_reader"
)

Code_converter_agent = create_agent(
    LLM_PLATFORM,
    "You are an expert in code transformation and migration, particularly in converting"
    " PHP applications to Spring Boot. Your task is to read the PHP file from the specified"
    " path and convert it into a fully functional Spring Boot application."
    " The converted application should follow Spring Boot best practices, including"
    " the use of appropriate annotations, configuration, and structuring. Ensure that all"
    " functionalities, endpoints, and business logic present in the PHP code are accurately"
    " replicated in the Spring Boot application. Additionally, handle any necessary"
    " dependency injections, database migrations, and security configurations required"
    " for a smooth transition from PHP to Spring Boot. After completing the conversion,"
    " output the transformed code in the appropriate Java classes, preserving the application's"
    " functionality and improving maintainability.",
    tools=[default_tool],
)

Code_converter_node = functools.partial(
    agent_node,
    agent=Code_converter_agent,
    name="Code_converter",
    # output_parser=JavaCodeOutputParser(),
)


# Define the agent for writing the controller code
controller_writer_agent = create_agent(
    LLM_PLATFORM,
    "You are an expert in code transformation and migration, particularly in converting"
    " PHP applications to Spring Boot"
    " You are an expert in generating and writing Spring Boot controller code. Generate"
    " the controller code based on the provided inputs and write it to the specified file.",
    [write_controller_code],
)

controller_writer_node = functools.partial(
    agent_node,
    agent=controller_writer_agent,
    name="Controller_Writer",
)

workflow = StateGraph(AgentState)
workflow.add_node("Initialization", initialization_node)
workflow.add_node("Testing", testing_node)
workflow.add_node("File_reader", file_reader_node)
# workflow.add_node("Code_converter", Code_converter_node)
workflow.add_node("Controller_Writer", controller_writer_node)
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
                content=f"Initialize spring boot application, the base directory is ./generate_spring_app."
                " write controller, services, repositories. file path of PHP `/Users/aj/development/python/langgraph-example/src/ApsAdminCompliaceController.php`"
            )
        ]
    },
    {"recursion_limit": 20},
):
    # if "__end__" not in s:
    print(s)
    print("----")

# /deps/langgraph-example/src/ApsAdminCompliaceController.php
