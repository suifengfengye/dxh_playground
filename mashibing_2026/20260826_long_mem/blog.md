# 1. 处理上下文爆炸的策略

- 消息截断
- 消息删除
- 消息摘要
- 自定义策略

## 1.1 消息截断

就是保留最近几条消息，可以在 @before_model中间件 中处理，比如保留最近N条信息。
消息截断的注意事项：

1. N的定义
2. 不破坏对话链：如一个ReaAct循环中，保留了一条 ToolMessage，这会让LLM理解不了上下文。

## 1.2 消息删除

选择性删除消息。比如检测掉用户的指令，需要删除之前对话的内容。
那么可以使用 RemoveMessage() 将所有历史信息删除。

```python

RemoveMessage(id=REMOVE_ALL_MESSAGES)
```

举例说明：检测到用户要删除整个历史记录的时候，使用 REMOVE_ALL_MESSAGES 将会话历史删除。

## 1.3 消息摘要

使用大模型进行总结，减少上下文。使用 SummarizationMessage() 中间件进行摘要处理。

```python
from langchain.agents.middleware import SummarizationMiddleware
SummarizationMiddleware(
    model="ollama:qwen3:latest", # 摘要生成模型 
    trigger=("tokens", 4000), # 触发条件：token ≥4000 
    keep=("messages", 20) # 保留最近20条消息 
)

SummarizationMiddleware( 
    model=deepseek_llm, 
    trigger=('messages',5), # 当消息数量超过5条时触发总结 
    keep=('messages', 2), # 保留最后2条消息 
    summary_prompt="请总结以下对话内容：{messages}" 
)
```

举例：在多轮对话中，检测 SummarizationMiddleware 的触发条件。

## 1.4 自定义策略

该方式可以解决标准方案（如消息截断、删除、摘要）无法覆盖的复杂场景（如一些场景中对话历史中包含文本、图片、文件多种信息时，需要根据需要动态保留哪些内容）。

可以通过中间件@before_model/@after_model/@wrap_model_call 来实现。

举例：通过自定义策略，使用 @after_model 实现一个 SummarizationMiddleware。


# 2. 
