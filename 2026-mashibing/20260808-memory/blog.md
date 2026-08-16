# 1. 短期记忆介绍

短期记忆能够让你的AI应用程序在一个线程/会话当中，记住之前的交互信息。

举一个没有记忆的例子：

```python
from langchain.agents import create_agent

# 使用本地启动的ollama+qwen3提供LLM服务
agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[]
)

resp1 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！我的名字叫张三！"
        }
    ]
})

print(resp1)

print("-" * 100)

resp2 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！请问我叫什么名字"
        }
    ]
})

print(resp2)
```

在没有运行之前，大家猜猜看，resp2的回答中会知道“我的名字叫张三吗”？ 为什么？

答案：当然是不知道。因为agent的两次调用之间没有任何关联，第二次提问，并没有将第一轮的对话内容传递给LLM。

所以就引出了“记忆”这个概念，目的就是让LLM知道之前的对话内容。

为此需要有一个地方存储历史对话信息列表！在langchain当中，使用 checkpointer 来存储记忆。

checkpointer是一个抽象概念，它可以是：
1. 内存
    使用 InMemorySaver (langgraph.checkpoint.memory)。存储在内存中有一个缺点就是，会话关闭之后，信息就会丢失。
2. 关系型DB
    将历史会话信息存储到关系型数据库(如mysql/postgressql/sqlite)中，会话关闭之后就不会丢失。
3. 非关系型DB 
    将历史会话信息存储到关系型数据库(如mongodb)中，会话关闭之后就不会丢失。

磁盘、关系型DB和非关系型DB，都能够在会话结束后，不丢失历史会话内容。那这个是不是就可以称为“长期记忆”了？??

# 2. 短期记忆存储

## 2.1 存储到内存中

langchain提供了 InMemorySaver 这个类来将记忆存储到内存当中。具体使用：

```python
...

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    checkpointer=InMemorySaver() # [add 1]. create_agent()方法含有checkpointer参数，将 InMemorySaver 的实例传入。
)

# [add 2] 增加配置，thread_id是每次会话的唯一标识，相同标识会话信息，langchain会整合到一个会话历史中
config = {"configurable": {"thread_id": "daxiaohan_01"}}

resp1 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！我的名字叫张三！"
        }
    ]
}, config=config) # [add 3] 每次调用时，将config传入

print(resp1)

print("-" * 100)

resp2 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！请问我叫什么名字"
        }
    ]
}, config=config) # [add 4] 每次调用时，将config传入

print(resp2)
```

这段代码中的 [add 1-4] 这几个地方的配置，就能让agent具备短期记忆能力。运行这段代码，会看到resp2的输出中，agent已经知道我的名字信息。

## 2.2 存储到关系型DB中

【前提】：大家需要先安装好mysql DB。langgraph-checkpoint-mysql要求mysql DB的版本不能太高，笔者使用8.4的版本能work，26.x版本会报错！

我们使用mysql为例说明。

### 2.2.1 安装依赖 langgraph-checkpoint-mysql

文档参考：https://pypi.org/project/langgraph-checkpoint-mysql/

```shell
pip install pymysql langgraph-checkpoint-mysql
```

### 2.2.2 代码实现
```python
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

# 1. 创建连接mysql到checkpointer
DB_URI = "mysql+pymysql://root:123456@localhost:3306/mysql?charset=utf8mb4"
with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:
    # 2. 在mysql数据库中进行初始化设置，如果发现已经初始化过，则不处理。
    checkpointer.setup()

    # 3. 将checkpointer传递给 create_agent
    agent = create_agent(
        model="ollama:qwen3:latest",
        tools=[],
        checkpointer=checkpointer
    )
```


## 2.3 存储到非关系型DB中

【前提】：需要先安装好 monogodb 数据库。
以 mongodb 为例子来说明。

### 2.3.1 安装依赖

文档参考：https://pypi.org/project/langgraph-checkpoint-mongodb/

```shell
# pip install -U langgraph-checkpoint-mongodb
pip install -U pymongo langgraph-checkpoint-mongodb
```

### 2.3.2 代码

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

# write_config = {"configurable": {"thread_id": "1", "checkpoint_ns": ""}}
# read_config = {"configurable": {"thread_id": "1"}}

MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "checkpoint_example"

with MongoDBSaver.from_conn_string(MONGODB_URI, DB_NAME) as checkpointer:
    ...
    # 其他代码也和 2.2 一样
```

# 3. 自定义Agent状态

之前看到 agent 的信息，全部都在 messages 当中。如果需要自定义除了messages之外的状态信息，要怎么办？

langchain也提供了对应的方式。在 create_agent() 方法中有一个 state_schema 参数，使用这个参数，可以自定义除 messages 之外的信息，并在 invoke() 时传入，langchain就会把这些信息也保存起来。

```python
from langchain.agents import create_agent, AgentState

class CustomAgentState(AgentState):
    user_id: str
    preferences: dict

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    state_schema=CustomAgentState
)

config = {"configurable": {"thread_id": "daxiaohan_01"}}

result = agent.astream({
    "messages": [
            {
                "role": "user",
                "content": "您好！我的名字叫张三！"
            }
    ],
    "user_id": "daxiaohan_01",
    "preferences": {
        "hobby": "旅游、看书、搞钱!"
    }
}, 
stream_mode="messages",
config=config)

async for item in result:
    ...
```

## 3.1 tool 获取/修改自定义状态信息

```python
@tool
def get_user_info(runtime: ToolRuntime):
    """
    获取用户信息。
    Args:
        runtime: 运行时实例对象
    """
    # print(f"@tool runtime:{runtime}")

    user_id = runtime.state["user_id"]
    level = runtime.state["level"]
    preferences = runtime.state["preferences"]

    return f"用户ID:{user_id}, 用户等级:{level}, 用户偏好:{preferences}"

@tool
def update_user_info(runtime: ToolRuntime, user_id: str, level: str, preferences: dict):
    """
    修改用户信息:
    Args:
        runtime: 工具运行时实例
        user_id: 用户ID
        level：用户等级
        preferences:用户偏好
    """
    print(f"update_user_info:{user_id}, {level}, {preferences}")
    if not user_id or not level or not preferences:
        return Command(update={
            "messages": [ToolMessage(
                    content="没有对应的用户信息",
                    tool_call_id= runtime.tool_call_id
                )
            ]
        })

    return Command(update={
            "messages": [ToolMessage(
                    content = "用户信息已经更新啦!!!!->大小寒_02",
                    tool_call_id = runtime.tool_call_id
                )],
            "user_id": "大小寒_02",
            "level": "NORMAL",
            "preferences": {
                "hobby": "自媒体、写代码！!"
            }
        })

agent = create_agent(
        model="ollama:qwen3:latest",
        tools=[get_user_info, update_user_info],
        state_schema=CustomAgentState,
        checkpointer=InMemorySaver()
    )
config = {"configurable": {"thread_id": "daxiaohan_01"}}

result = agent.invoke({
        "messages": [
                {
                    "role": "user",
                    "content": "我的用户信息是什么？"
                }
        ],
        "user_id": "daxiaohan_01",
        "level": "VIP",
        "preferences": {
            "hobby": "旅游、看书、搞钱!"
        }
    },
    config=config)

print(result)

result = agent.invoke({
        "messages": [
                {
                    "role": "user",
                    "content": ("帮我修改用户信息,用户ID:大小寒_02,用户等级:NORMAL,用户偏好：自媒体、写代码！!")
                }
        ],
        "user_id": "daxiaohan_01",
        "level": "VIP",
        "preferences": {
            "hobby": "旅游、看书、搞钱!"
        }
    },
    config=config)

print(result["messages"][-1].content)

```

## 3.2 middleware 获取/修改自定义状态信息

<!-- todo -->