from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


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

config = {"configurable": { "thread_id": "session_dxh_01" }}

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "请删除用户123的信息"
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
            
        if resume_cmd:
            resp = agent.invoke(resume_cmd, config=config, version="v2")
            print(f"最终结果:{resp.value["messages"][-1].content}")
            # print("=" * 100)
            # print('打印全部消息:')
            # print(resp)
            # print("=" * 100)

else:
    print('结束')
