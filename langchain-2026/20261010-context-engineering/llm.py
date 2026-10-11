from langchain.chat_models import init_chat_model

# DeepSeek V4 默认开启 thinking（思考）模式，而 thinking 模式不支持
# tool_choice="required"；LangChain 的 ToolStrategy（以及 provider 原生结构化输出）
# 会强制下发该参数，从而报 400: Thinking mode does not support this tool_choice。
# 这里显式关闭思考模式。非标准参数必须放在 extra_body 里。
ds_llm = init_chat_model(
    "deepseek-v4-flash",
    extra_body={"thinking": {"type": "disabled"}},
)

# 手动设置 model profile，让 SummarizationMiddleware 走 fraction 模式而非 fallback。
# deepseek-v4-flash 默认 profile 为空 {}，SummarizationMiddleware 会走 fallback：
#   trigger=170000 tokens、keep=6 messages —— 演示不现实。
# 设 max_input_tokens=8000 后，trigger=8000*0.85=6800 tokens（≈27200 字符），
# keep=8000*0.10=800 tokens，几轮对话 + 一个大工具结果就能触发自动摘要。
ds_llm.profile = {"max_input_tokens": 8000}
