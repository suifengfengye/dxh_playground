import chroma

client = chroma.Client()

collection = client.get_collection("lc_test")
if not collection:
    collection = client.create_collection("lc_test")

collection.add(
    ids=["id1", "id2"],
    documents=["你好，世界！", "你好，chroma!"],
)

result = collection.query(
    query_texts=["你好，世界！"],
    n_results=2,
)

print(result)