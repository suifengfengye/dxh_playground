def cook():
    print("1. 热锅下油")
    yield "酱油没了，我先去买"      # 在这里「暂停」，控制权交回调用方
    print("2. 酱油回来了，接着炒")
    yield "炒好了，装盘"
    print("3. 上桌")

c = cook()
print("调用 cook() 拿到的不是菜，而是一个对象:", c)
print("第一次 next ->", next(c))
print("……等待过程中，我可以去顺手把米饭煮上")
print("第二次 next ->", next(c))
