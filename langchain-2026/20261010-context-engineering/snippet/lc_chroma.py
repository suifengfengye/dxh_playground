import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import pydantic import SecretStr

ZAI_API_KEY = os.environ.get("ZAI_API_KEY")
print(f"ZAI_API_KEY: {ZAI_API_KEY}")

embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=SecretStr(ZAI_API_KEY),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

embedding = OpenAIEmbeddings()

vector_store = Chroma.from_documents([], embedding, persist_directory="./chroma_fashion")
retriever = vector_store.as_retriever(search_kwargs={"k":2}) # 只取top2，控制上下文长度
result = retriever.invoke("黑色")
