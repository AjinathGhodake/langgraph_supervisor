from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from constants import MEMBERS, OPTIONS


system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers:  {MEMBERS}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When status and result as finished,"
    " respond with FINISH."
)

supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        # MessagesPlaceholder(variable_name="agent_scratchpad"),
        (
            "system",
            "Given the conversation above, who should act next?"
            f" Or should we FINISH? Select one of: {OPTIONS}",
        ),
    ]
).partial(options=str(OPTIONS), members=", ".join(MEMBERS))
