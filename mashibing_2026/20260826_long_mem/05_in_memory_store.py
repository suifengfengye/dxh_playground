from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

namespace = ("user_123", "preferences")

# 1. 存储数据

store.put(namespace, "fruit", { "like": ["orange", "banana"], "dislike": ["apple"] })
store.put(namespace, "sport", { "like": ["basketball", "football"], "dislike": ["pingpong"] })
store.put(namespace, "color", { "like": ["red", "yellow"], "dislike": ["绿色"] })

# 2. 获取数据

fruit_result = store.get(namespace, "fruit")

print(fruit_result)
print("*" * 80)
# 3. 搜索数据

# query 参数在默认的 InMemoryStore() 下不会做关键词搜索或语义搜索。
# 只有配置了 index + embedding 后，query 才会真正参与向量检索。
search_result = store.search(namespace, query="绿色")
print("store.search(query='绿色') 的结果：")
print(search_result)
print("*" * 80)

# 如果只是想做当前 demo 里的字符串包含搜索，最直接的是先取出条目再手动过滤。
all_items = store.search(namespace)
matched_items = [item for item in all_items if "绿色" in str(item.value)]

print("手动过滤包含 '绿色' 的结果：")
print(matched_items)
