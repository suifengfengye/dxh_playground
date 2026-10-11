import hashlib
import json
import os
from pathlib import Path

import pymysql

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.summarization import create_summarization_tool_middleware
from langchain.agents import AgentState
from langchain.tools import ToolRuntime, tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from pydantic import BaseModel, SecretStr
from langchain.agents.middleware import before_model
from langgraph.store.mysql import PyMySQLStore

from llm import ds_llm
# from demo_tools import DEMO_TOOLS

# 海量商品信息全部卸载到向量库，不常驻prompt！
# goods_data = [
#     "浅灰针织连衣裙：面料纯棉，S/M/L码，适合通勤，价格299元；买家评价：版型显瘦，微透，建议内搭吊带；7天无理由退换，现货充足。",
#     "牛仔直筒长裤：水洗牛仔，弹力中等；尺码25-30码；价格349元；评价：裤长偏长，160cm需要裁边；现货充足，支持免费改裤长。"
#     "白色短款小西装：聚酯纤维+少量氨纶；S/M码；459元；评价：容易粘毛，适合搭配连衣裙；库存仅剩M码。",
#     "休闲帆布鞋：帆布，35-40码；199元；评价：偏大半码，脚宽建议选小一码；现货充足。",
# ]
goods_data = [
    # ---------------- 女装 ----------------
    Document(page_content="浅灰针织连衣裙：面料纯棉，S/M/L码，适合通勤，价格299元；买家评价：版型显瘦，微透，建议内搭吊带；7天无理由退换，现货充足。"),
    Document(page_content="牛仔直筒长裤：水洗牛仔，弹力中等；尺码25-30码；价格349元；评价：裤长偏长，160cm需要裁边；现货充足，支持免费改裤长。"),
    Document(page_content="白色短款小西装：聚酯纤维+少量氨纶；S/M码；459元；评价：容易粘毛，适合搭配连衣裙；库存仅剩M码。"),
    Document(page_content="休闲帆布鞋：帆布，35-40码；199元；评价：偏大半码，脚宽建议选小一码；现货充足。"),
    Document(page_content="黑色高腰阔腿裤：垂感西装面料，无弹力；S/M/L/XL码；价格289元；评价：显腿长、遮肉，裤腰偏紧，建议按腰围选码；现货充足。"),
    Document(page_content="米白泡泡袖雪纺衫：雪纺+聚酯纤维，轻薄透气；S/M/L码；价格169元；评价：夏天穿凉快，袖子显肩宽，肩宽人群慎选；现货充足。"),
    Document(page_content="卡其风衣中长款：棉+聚酯纤维，可拆内胆；S/M/L/XL码；价格599元；评价：版型挺括，长度到膝盖下，158cm小个子需谨慎；库存紧张。"),
    Document(page_content="奶咖色针织开衫：羊毛混纺，柔软亲肤；均码偏宽松；价格239元；评价：起球轻微、洗后略变形，建议手洗；现货充足。"),
    Document(page_content="黑色皮质半身裙：PU皮，内衬聚酯纤维；S/M/L码；价格259元；评价：显身材，坐下略紧，冬季偏冷需搭打底裤；现货充足。"),
    Document(page_content="浅蓝牛仔短外套：水洗牛仔，硬挺；S/M/L码；价格279元；评价：做旧感好、百搭，肩线偏窄；现货充足。"),
    Document(page_content="白色厚底小白鞋：真皮拼接，鞋底3cm；35-40码；价格429元；评价：显高、百搭，鞋底偏硬需磨合；现货充足。"),
    Document(page_content="条纹针织半身长裙：针织，弹力大；均码；价格199元；评价：包臀显瘦，走路有束缚感；库存紧张。"),
    # ---------------- 男装 ----------------
    Document(page_content="男士纯色牛津纺衬衫：100%棉，免烫处理；S/M/L/XL/XXL码；价格229元；评价：挺括不皱，领口偏紧，脖子粗建议大一码；现货充足。"),
    Document(page_content="男士修身直筒牛仔裤：水洗牛仔，弹力中等；尺码28-36码；价格329元；评价：版型正，大腿处偏紧，腿粗建议选直筒加大码；现货充足。"),
    Document(page_content="男士休闲工装裤：棉+锦纶，多口袋；尺码29-38码；价格299元；评价：耐穿百搭，裤腿偏肥，偏瘦人群显松；现货充足。"),
    Document(page_content="男士连帽卫衣：棉混纺抓绒，内里加绒；M/L/XL/XXL码；价格259元；评价：保暖舒适，洗后缩水约一码，建议买大一号；现货充足。"),
    Document(page_content="男士轻薄羽绒服：白鸭绒填充，含绒量90%；M/L/XL/XXL码；价格699元；评价：轻便保暖，修身版型，偏胖人群建议大一码；库存紧张。"),
    Document(page_content="男士商务正装西裤：聚酯纤维+羊毛，垂感好；尺码29-38码；价格399元；评价：显腿直、适合面试，需干洗；现货充足。"),
    Document(page_content="男士短袖POLO衫：珠地棉，透气；M/L/XL/XXL/XXXL码；价格189元；评价：商务休闲两用，领子易变形，建议手洗；现货充足。"),
    Document(page_content="男士运动跑鞋：网面+橡胶大底，缓震中底；39-45码；价格359元；评价：轻便透气，鞋头偏窄，脚宽建议选大一码；现货充足。"),
    Document(page_content="男士夹克外套：涤纶防风面料，防泼水；M/L/XL/XXL码；价格449元；评价：户外休闲皆可，袖长偏长，170cm以下建议选S；库存紧张。"),
    Document(page_content="男士针织毛衣：羊毛混纺，圆领；M/L/XL/XXL码；价格279元；评价：柔软不起球，洗后轻微变形；现货充足。"),
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

PREFERENCE_KEY = "preference"

def get_preference_namespace(user_id:str) -> tuple[str, str]:
    return ('preference', user_id)

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

@tool
def export_full_catalog() -> str:
    """
    导出完整的商品目录报表（含所有商品的详细信息）。
    当用户要求「导出全部商品」「看完整商品清单」「导出报表」时调用。
    """
    lines = ["# 服装商城完整商品目录", ""]
    for i, doc in enumerate(goods_data, 1):
        lines.append(f"## 商品 {i}")
        lines.append(doc.page_content)
        lines.append("-" * 60)
        lines.append("")
    report = "\n".join(lines)
    # 默认 22 条商品约 3000 字符，远不够 80000（≈20000 token）。
    # 这里循环拼接至超过阈值，确保触发 deepagents 的 offload 机制。
    if len(report) < 90000:
        report = (report + "\n") * (90000 // len(report) + 1)
    return report

@tool
def get_user_preference(runtime: ToolRuntime) -> str:
    """
    返回存储下来的用户偏好信息，包括但不限于以下用户的信息：
    - 性别
    - 年龄
    - 身高
    - 体重
    - 居住地/籍贯
    - 教育背景
    等等
    return 用户偏好信息字符串
    """
    store = runtime.store
    user_id = runtime.context.user_id
    namespace = get_preference_namespace(user_id)
    preference = store.get(namespace, PREFERENCE_KEY) or ""
    print(f"@@@get_user_preference, preference: {preference}")
    return preference

@tool
def store_user_preference(preference: str, runtime: ToolRuntime):
    """
    存储用户的偏好信息，包括但不限于以下用户的信息：
    - 性别
    - 年龄
    - 身高
    - 体重
    - 居住地/籍贯
    - 教育背景
    等等
    Args:
        preference: 用户偏好信息
    """
    store = runtime.store
    user_id = runtime.context.user_id
    namespace = get_preference_namespace(user_id)
    cur_content = store.get(namespace,PREFERENCE_KEY)
    if not preference:
        return cur_content
    content = f"{cur_content}, {preference}" 
    store.put(namespace, PREFERENCE_KEY, content)
    print(f"@@@store_user_preference, cur_content: {cur_content}, content: {content}")
    return content

# 去重集合：静态上下文按 hash 去重，消息按 id 去重
_seen_context_hashes: set[str] = set()
_seen_msg_ids: set[str] = set()

@before_model
def handle_before_model(state: AgentState, runtime: Runtime):
    """每次模型调用前，将 messages + 静态上下文写入 ./messages.jsonl，按 hash / id 去重。"""
    log_path = Path(__file__).resolve().parent / "messages.jsonl"

    # ---- 1. 静态上下文（system_prompt + AGENTS.md + skills），按内容 hash 去重 ----
    memory_contents: dict = state.get("memory_contents") or {}
    skills_metadata = state.get("skills_metadata") or []

    def _skill_info(s):
        if isinstance(s, dict):
            return {k: s.get(k) for k in ("name", "description", "path") if k in s}
        return {k: getattr(s, k, None) for k in ("name", "description", "path")}

    static_context = {
        "system_prompt": SYSTEM_PROMPT,
        "memory_contents": memory_contents,   # dict[str, str]，key=路径 value=文件内容
        "skills": [_skill_info(s) for s in skills_metadata],
    }
    context_hash = hashlib.md5(
        json.dumps(static_context, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()

    with open(log_path, "a", encoding="utf-8") as f:
        if context_hash not in _seen_context_hashes:
            _seen_context_hashes.add(context_hash)
            f.write(json.dumps(
                {"type": "static_context", "hash": context_hash, **static_context},
                ensure_ascii=False,
            ) + "\n")

        # ---- 2. 动态消息，按 message id 去重 ----
        for msg in state.get("messages", []):
            msg_id = getattr(msg, "id", None) or str(msg)
            if msg_id in _seen_msg_ids:
                continue
            _seen_msg_ids.add(msg_id)
            f.write(json.dumps(
                {"type": "message", "id": msg_id,
                 "role": getattr(msg, "type", "unknown"),
                 "content": str(getattr(msg, "content", ""))},
                ensure_ascii=False,
            ) + "\n")

    return None


class Context(BaseModel):
    user_id: str

SYSTEM_PROMPT = """
你是线上服装商城穿搭导购AI助手。
1. 如果用户询问衣服、鞋子、裤子、外套等服装的价格、面料、尺寸、库存，调用 search_product 工具查询
2. 如果没有查询到相关信息，则直接告诉用户暂时没有该商品，禁止编造
3. 穿搭建议简洁接地气，面向普通消费者
4. 不要一次性推荐所有商品，根据用户需求推荐
5. 涉及尺码推荐时，按 size-guide 技能的流程处理；涉及整套场合搭配时，按 outfit-styling 技能处理
6. 明确要比较两件商品时用 compare_products；问优惠满减时用 promotion_advisor
7. 用户要求导出全部商品、完整清单、报表时，调用 export_full_catalog 工具
8. 用户说"压缩对话""精简上下文""compact"时，调用 compact_conversation 工具
"""

# skills：按需加载的「怎么做」。元数据常驻，正文等真正需要时才 read_file 展开。
# backend 用 FilesystemBackend 从磁盘读取 skills 与 memory。
PROJECT_ROOT = Path(__file__).resolve().parent

DB_URI = "mysql+pymysql://root:123456@localhost:3306/mysql?charset=utf8mb4"

# 注意：不要用 `with PyMySQLStore.from_conn_string(DB_URI) as store`。
# 那个 contextmanager 会在 with 块退出时关闭底层 pymysql 连接；
# 而 agent 是在 with 块里创建、之后才被 stream_main.py 使用，
# 结果工具调用时连接已关闭 -> pymysql.err.InterfaceError: (0, '')。
# 这里直接建一条进程级长连接，交给 store 持有。
_conn = pymysql.connect(
    **PyMySQLStore.parse_conn_string(DB_URI),
    charset="utf8mb4",
    autocommit=True,
)
store = PyMySQLStore(_conn)
store.setup()  # 幂等：确保建表与迁移，表已存在时无副作用

# ---- 摘要配置 ----
# 自动摘要：create_deep_agent 默认已包含 SummarizationMiddleware。
#   llm.py 里设了 ds_llm.profile = {"max_input_tokens": 8000}，
#   所以默认中间件走 fraction 模式：trigger=6800 tokens、keep=800 tokens。
#   不需要手动创建或 excluded_middleware。
#
# 按需摘要：通过 create_summarization_tool_middleware 给 agent 加 compact_conversation 工具，
#   用户说"压缩对话"时 agent 主动调用它触发摘要。
#   两者共享同一个 summarization 引擎和 state。
_fs_backend = FilesystemBackend(root_dir=str(PROJECT_ROOT), virtual_mode=True)

compact_tool_mw = create_summarization_tool_middleware(
    model=ds_llm,
    backend=_fs_backend,
)

agent = create_deep_agent(
    model=ds_llm,
    tools=[search_product, export_full_catalog, get_user_preference, store_user_preference],
    skills=["/skills/"],
    backend=_fs_backend,
    memory=["/AGENTS.md"],
    system_prompt=SYSTEM_PROMPT,
    middleware=[handle_before_model, compact_tool_mw],
    checkpointer=InMemorySaver(),
    store=store,
    context_schema=Context,
)
