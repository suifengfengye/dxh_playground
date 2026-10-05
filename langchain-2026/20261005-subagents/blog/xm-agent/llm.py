"""模型配置 —— 本目录自带，不依赖仓库里其他任何文件。

DeepSeek V4 默认开启 thinking（思考）模式，而 thinking 模式不支持
tool_choice="required"；LangChain 的 ToolStrategy（以及 provider 原生结构化输出）
会强制下发该参数，从而报 400: Thinking mode does not support this tool_choice。
这里显式关闭思考模式。非标准参数必须放在 extra_body 里。
"""

from langchain.chat_models import init_chat_model

ds_llm = init_chat_model(
    "deepseek-v4-flash",
    extra_body={"thinking": {"type": "disabled"}},
)
