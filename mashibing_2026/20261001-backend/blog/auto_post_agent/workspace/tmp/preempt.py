import threading, time

start = time.perf_counter()

def busy():
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 1.5:
        pass                      # 纯计算死占 CPU，中途「不让出」
    print(f"t={time.perf_counter()-start:.2f}s 忙线程自己跑完了")

th = threading.Thread(target=busy)
th.start()
time.sleep(0.3)
print(f"t={time.perf_counter()-start:.2f}s 另一个线程照样拿到了 CPU（内核抢走的）")
th.join()
