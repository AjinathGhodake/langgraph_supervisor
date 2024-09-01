from functools import lru_cache
from langchain_openai import ChatOpenAI

from langchain_ollama.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent

from main import AgentState


@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "ollama":
        model = ChatOllama(temperature=0, model="llama3.1")
    elif model_name == "groq":
        model = ChatGroq(temperature=0, model="llama-3.1-70b-versatile")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    return model


def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


def create_agent(
    provider_name: str,
    system_prompt: str,
    tools: list = [],
    functions: list = [],
):
    # Ensure 'system_prompt' is either a pre-constructed prompt or string
    if isinstance(system_prompt, ChatPromptTemplate):
        prompt = system_prompt
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    model = _get_model(provider_name)
    if functions:
        model.bind_functions(functions=functions)

    agent = create_openai_tools_agent(model, tools, prompt)

    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def update_application_structure(state: AgentState, result):
    state.set_application_structure(
        {
            "project_path": result.get("project_path"),
            "key_files": result.get("key_files", []),  # Adjust based on actual output
        }
    )
