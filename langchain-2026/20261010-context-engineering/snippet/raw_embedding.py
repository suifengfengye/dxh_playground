import os
import requests

model = "embedding-3"

ZAI_API_KEY = os.environ.get("ZAI_API_KEY")
print(f"ZAI_API_KEY: {ZAI_API_KEY}")

payload = {
    "model": "embedding-3",
    "input": "你好，世界！",
    "dimensions": 2048,
}

header = {
    "Authorization": f"Bearer {ZAI_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post("https://open.bigmodel.cn/api/paas/v4/embeddings", json=payload, headers=header)

print(response.text)