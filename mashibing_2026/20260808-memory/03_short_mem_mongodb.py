from langchain.agents import create_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

# 1. 创建连接mysql到checkpointer
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "langchain_db"

with MongoDBSaver.from_conn_string(MONGODB_URI, DB_NAME) as checkpointer:
    agent = create_agent(
        model="ollama:qwen3:latest",
        tools=[],
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": "daxiaohan_01"}}

    resp1 = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "您好！我的名字叫张三！"
            }
        ]
    }, config=config)

    print(resp1["messages"][-1].content)

    print("-" * 100)

    resp2 = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "您好！请问我叫什么名字"
            }
        ]
    }, config=config)

    print(resp2["messages"][-1].content)