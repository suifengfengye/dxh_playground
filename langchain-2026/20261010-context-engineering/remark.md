1. chroma + embedding + langchain_core的Document
   
本质：做一个向量检索功能 
-> 数据 -> embedding -> 向量数据库 chroma -> 检索实现

（1）假数据: -> 数据寻找困难 -> AI生成
[]

（2）做成向量 chroma: embedding -> chroma
ds没有embedding，ollama下载了，主要是慢！zhipu支持embedding

- embedding
- chroma
- langchain-chroma

(3) chroma检索

data_list = []
embedding = OpenAIEmbeddings(
    api_key=ZAI_API_KEY,
    base_url="https://api.zhipu.ai/v1",
    model="embedding-3",
)
embedding.embed_documents(data_list)
embedding.embed_query("test")

vector_store = Chroma.from_documents(data_list, embedding=embedding, collection_name="test", persist_directory="test")
retriver = vector_store.as_retriever()
retriver.invoke("test")

1. AGENTS.md 的编写+使用+观察

冷启动需要使用的md文件/提示词文件

2. skills的编写+使用+观察



3. 如果获取父级目录

from pathlib import Path

PROJECT_ROOT = Path.resolve(__file__).parent

4. 连接 mysql store
from pymysql
from langchain.store.mysql import PyMySQLStore

DB_URI = "mysql+pymysql://root:123456@localhost:3306/mysql?charset=utf8mb4"
_conn = pymysql.connect(
    **PyMySQLStore.parse_conn_string(DB_URI),
    charset='utf8mb4',
    autocommit=True,
)
store = PyMySQLStore(_conn)
store.setup()


1. 触发自动总结和摘要
   
   构造一个tool，读取大文件！！！

2. 按规则总结+摘要

from deepagents.backend import FilesystemBackend
from deepagents.middleware.summarization import create_summarization_tool_middleware

_backend = FilesystemBackend(root_path="/path/to/summary", virtual_model=True)

middleware = create_summarization_tool_middleware(
    model=ds_llm,
    backend=_backend
)
