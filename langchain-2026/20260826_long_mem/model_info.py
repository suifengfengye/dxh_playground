import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

deepseek_model = init_chat_model("deepseek-v4-flash")