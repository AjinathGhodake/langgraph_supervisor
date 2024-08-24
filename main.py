from my_agent.agent import graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="test the spring boot application, the path of application is /Users/aj/development/python/langgraph-example/generated_spring_app/generated_spring_app"
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")
