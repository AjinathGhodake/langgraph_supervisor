from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


members = ["Researcher", "Coder"]
options = ["FINISH"] + members
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers:  {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            f" Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))
