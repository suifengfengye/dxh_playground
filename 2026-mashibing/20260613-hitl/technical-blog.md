# 1. 什么是HITL
HITL是 human-in-the-loop的简称。它是一种在AI Agent执行过程中引入人工操作的机制。
它的核心理念是：有些重要操作不应该由AI Agent来决策，而是由人来决策。

常见的重要操作：

1. 数据库操作：比如删除用户。
2. 文件系统操作：删除文件、删除目录等高危行为。
3. 资金交易：退款、调整定价等等。 

# 2. HITL的使用示例
在langchain中，HITL是一中间件的形式存在 -- HumanInTheLoopMiddleware。
要在langchain中AI Agent中添加 HumanInTheLoopMiddleware 非常简单。

```python
# langchain版本: 1.3.9
# langgraph版本：1.2.5
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# 1. 使用 @tool 装饰器定义了两个工具 query_user + delete_user,其中delete_user是高危操作。
@tool
def query_user(user_id: str):
    """查询用户信息"""
    return f"查询到具体的用户信息返回"

@tool
def delete_user(user_id: str):
    """删除用户信息"""
    return f"删除用户{user_id}的信息以及相关记录成功"

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[query_user, delete_user],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "query_user": False,
                "delete_user": True
            }
        )
    ],
    checkpointer=InMemorySaver()
)

# 2. 调用配置，config告诉运行时：“这次调用该怎么执行、属于哪条会话、怎么恢复状态”
config = {"configurable": { "thread_id": "session_dxh_01" }}

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "请删除用户123的信息" # 模拟一个高危操作
            },
        ]
    },
    config=config,
    version="v2"
)

if result.interrupts:
    print(f"======[Agent 中断执行，等待输入]=========")
    action_requests = result.interrupts[0].value["action_requests"]
    review_configs = result.interrupts[0].value["review_configs"]
    for index, req in enumerate(action_requests):
        # print(f"index:{index}, req:{req}")
        review_item = review_configs[index]
        allowed_decisions = review_item["allowed_decisions"]
        while True:
            decision = input(f"请输入,允许的输入 {allowed_decisions}:").strip().lower()
            if decision in allowed_decisions:
                break
            print(f"输入不正确，只允许输入:{allowed_decisions}, 您当前的输入为:{decision},请重新输入")

        if decision == 'approve':
            resume_cmd = Command(resume={
                "decisions": [
                    {
                        "type": "approve"
                    }
                ]
            })
        elif decision == 'reject':
            resume_cmd = Command(resume={
                "decisions": [
                    {
                        "type": "reject",
                        "message": "不能执行删除用户这种高危操作"
                    }
                ]
            })
        elif decision == "edit":
            user_id = input(f"请输入需要删除的用户ID:")
            resume_cmd = Command(resume={
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "delete_user",
                            "args": {"user_id": user_id}
                        }
                    }
                ]
            })
        elif decision == "respond":
            user_input = input(f"输入您的新要求:")
            resume_cmd = Command(resume={
                "decisions": [
                    {
                        "type": "respond",
                        "message": user_input
                    }
                ]
            })
        else:
            print("无操作，退出！")
        
        # 调用 invoke 恢复执行。
        if resume_cmd:
            resp = agent.invoke(resume_cmd, config=config, version="v2")
            print(f"最终结果:{resp.value["messages"][-1].content}")
            # print("=" * 100)
            # print('打印全部消息:')
            # print(resp)
            # print("=" * 100)

else:
    print('结束')
```
这段代码，首先使用 @tool 装饰器定义了两个工具 query_user + delete_user,其中delete_user是高危操作。
所以在 HumanInTheLoopMiddleware 的配置中，将 query_user设置为 False，delete_user 设置为 True。

这里需要留意的一点是 HITL 中间件，必须要配合 checkpointer 一起使用。否则会报错：

```shell
RuntimeError: Cannot use Command(resume=...) without checkpointer
```

这里的原因是中断执行，其实是将当前运行实例相关信息存储了起来，在HITL执行之后，再恢复之前的状态，所以 checkpointer 必须设置。

# 3. HITL的配置

HITL 中间件定义了四种内置的人工响应方式，每种对应不同的业务场景。

| **决策类型**      | **含义**                 | **使用场景示例**           |
| ----------------------- | ------------------------------ | -------------------------------- |
| **approve(批准)** | 原样执行工具调用               | 如：发送已确认无误的邮件         |
| **edit(修改)**    | 修改工具参数后执行             | 如：修改删除条件后再执行SQL      |
| **reject(拒绝)**  | 拒绝工具调用，附上反馈说明     | 如：拒绝不当的退款请求并说明原因 |
| **respond(回复)** | 跳过工具执行，直接返回人工回复 | 如：回答一个"询问用户"类型的工具 |

以上决策类型的设置，需要在创建 Agent 时引入 HumanInTheLoopMiddleware，并通过 interrupt_on 参数为每个工具配置中断策略。示例代码如下：

```python
agent = create_agent(
    model="gpt-5.4",
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # True 表示中断，允许所有决策类型（approve/edit/reject/respond）
                "write_file": True,
                # 自定义配置：只允许批准和拒绝，不允许编辑参数
                "execute_sql": {
                    "allowed_decisions": ["approve", "reject"],
                    "description":"工具中断描述的文本消息"
                },
                # False 表示自动放行，无需审批
                "read_data": False,
            },
            # 中断消息的前缀，最终显示为 "Tool execution pending approval: execute_sql..."
            description_prefix="Tool execution pending approval",
        ),
    ],
    # 必须配置检查点来持久化图状态
    checkpointer=InMemorySaver(),
)
```

以上示例代码中，关于HumanInTheLoopMiddleware中间件的配置参数解释如下：

* interrupt_on 是一个字典，键为工具名称，值为中断配置。值有三种可能：
  * True：对该工具启用中断，允许所有四种决策类型。
  * False：对该工具禁用中断，工具调用自动放行。
  * InterruptOnConfig 对象：精细控制，可指定 allowed\_decisions（允许的决策类型列表）和 description（自定义描述文本）。
* description_prefix 是中断消息的前缀，会被拼接到完整的提示信息中，例如 "Tool execution pending approval: execute\_sql with query='DELETE FROM...'"。单个工具可以通过 InterruptOnConfig 的 description 字段覆盖此前缀。

每个工具可用的决策类型取决于你在 interrupt\_on 中的配置。例如，对于 execute\_sql 你只允许 approve 和 reject，不允许 edit，这样即便人工介入也不能修改 SQL 语句——这是一种安全策略的精细控制。

# 4. HITL的设计原则

langchain给我们封装好了 HITL 中间件，我们使用起来也非常简单，这是使用框架的优势。
但同时我们也能看到，我们不知道langchain到底做了啥！为什么这么配置就可以了？
如果我们能脱离langchain框架，最小化实现一个HITL，应该就能明白它底层运行的逻辑。

## 4.1 架构设计要点

我们主要是模拟 HITL 流程，所以需要一个Agent运行时。同时为了

