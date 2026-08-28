from langchain.agents import create_agent
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

# 1. 创建连接mysql到checkpointer
DB_URI = "mysql+pymysql://root:123456@localhost:3306/mysql?charset=utf8mb4"
with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:
    # 2. 在mysql数据库中进行初始化设置，如果发现已经初始化过，则不处理。
    checkpointer.setup()

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