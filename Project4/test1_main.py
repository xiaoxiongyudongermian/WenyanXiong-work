import SM3
import OptimizatedSM3
from time import time

if __name__=="__main__":
    m1 = 'abcd' * 16
    m2 = 'abcd' * 16

    # 优化前
    t1 = time()
    for i in range(1000):
        SM3.SM3(m1)
    t2 = time()
    print("优化前进行1000次加密耗时:", t2 - t1, "秒")

    # 优化后
    t3 = time()
    for i in range(1000):
        OptimizatedSM3.SM3(m2)
    t4 = time()
    print("优化后进行1000次加密耗时:", t4 - t3, "秒")
