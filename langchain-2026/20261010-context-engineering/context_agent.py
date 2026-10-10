import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import SecretStr

from llm import ds_llm
from demo_tools import DEMO_TOOLS

# 海量商品信息全部卸载到向量库，不常驻prompt！
# goods_data = [
#     "浅灰针织连衣裙：面料纯棉，S/M/L码，适合通勤，价格299元；买家评价：版型显瘦，微透，建议内搭吊带；7天无理由退换，现货充足。",
#     "牛仔直筒长裤：水洗牛仔，弹力中等；尺码25-30码；价格349元；评价：裤长偏长，160cm需要裁边；现货充足，支持免费改裤长。"
#     "白色短款小西装：聚酯纤维+少量氨纶；S/M码；459元；评价：容易粘毛，适合搭配连衣裙；库存仅剩M码。",
#     "休闲帆布鞋：帆布，35-40码；199元；评价：偏大半码，脚宽建议选小一码；现货充足。",
# ]
goods_data = [
    Document(page_content="浅灰针织连衣裙：面料纯棉，S/M/L码，适合通勤，价格299元；买家评价：版型显瘦，微透，建议内搭吊带；7天无理由退换，现货充足。"),
    Document(page_content="牛仔直筒长裤：水洗牛仔，弹力中等；尺码25-30码；价格349元；评价：裤长偏长，160cm需要裁边；现货充足，支持免费改裤长。"),
    Document(page_content="白色短款小西装：聚酯纤维+少量氨纶；S/M码；459元；评价：容易粘毛，适合搭配连衣裙；库存仅剩M码。"),
    Document(page_content="休闲帆布鞋：帆布，35-40码；199元；评价：偏大半码，脚宽建议选小一码；现货充足。"),
]

# 向量模型：智谱 AI 提供 OpenAI 兼容接口，直接复用 OpenAIEmbeddings。
#   1. 去 https://open.bigmodel.cn 控制台创建 API Key（形如 xxxxxxxx.xxxxxxxx）
#   2. 终端执行：export ZAI_API_KEY=你的key
ZAI_API_KEY = os.environ.get("ZAI_API_KEY")
if not ZAI_API_KEY:
    raise RuntimeError(
        "缺少 ZAI_API_KEY 环境变量。\n"
        "  1) 打开 https://open.bigmodel.cn 创建 API Key\n"
        "  2) 执行 export ZAI_API_KEY=你的key\n"
        "  3) 重新运行"
    )

embedding = OpenAIEmbeddings(
    model="embedding-3",                               # 智谱向量模型，默认 2048 维
    api_key=SecretStr(ZAI_API_KEY),
    base_url="https://open.bigmodel.cn/api/paas/v4/",  # 智谱 OpenAI 兼容端点
    chunk_size=64,                                     # 智谱限制：单次最多 64 条
    check_embedding_ctx_length=False,                  # 关键！直接发原文，不走 tiktoken 分词
)
vector_store = Chroma.from_documents(goods_data, embedding, persist_directory="./chroma_fashion")
retriever = vector_store.as_retriever(search_kwargs={"k":2}) # 只取top2，控制上下文长度

@tool
def search_product(query: str) -> str:
    """
    服装商城商品检索工具。
    用户询问衣服面料、尺码、价格、库存、买家评价时调用。
    商品库海量数据全部卸载在向量库，只有调用工具才加载片段进入上下文。
    """
    docs = retriever.invoke(query)
    content = "\n".join([d.page_content for d in docs])
    # 增加裁剪：返回内容过长，截断，控制上下文token
    if len(content) > 600:
        content = content[:600] + "\n【内容过长，已截断】"
    return content

SYSTEM_PROMPT = """
你是线上服装商城穿搭导购AI助手。
1. 如果用户询问衣服、鞋子、裤子、外套等服装的价格、面料、尺寸、库存，调用 search_product 工具查询
2. 如果没有查询到相关信息，则直接告诉用户暂时没有该商品，禁止编造
3. 穿搭建议简洁接地气，面向普通消费者
4. 不要一次性推荐所有商品，根据用户需求推荐
5. 涉及尺码推荐时，按 size-guide 技能的流程处理；涉及整套场合搭配时，按 outfit-styling 技能处理
6. 明确要比较两件商品时用 compare_products；问优惠满减时用 promotion_advisor
"""

# skills：按需加载的「怎么做」。元数据常驻，正文等真正需要时才 read_file 展开。
# backend 用 FilesystemBackend 从磁盘读取 skills 与 memory。
PROJECT_ROOT = Path(__file__).resolve().parent

agent = create_deep_agent(
    model=ds_llm,
    tools=[search_product, *DEMO_TOOLS],
    skills=["/skills/"],
    backend=FilesystemBackend(root_dir=str(PROJECT_ROOT), virtual_mode=True),
    memory=["/AGENTS.md"],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver()
)
