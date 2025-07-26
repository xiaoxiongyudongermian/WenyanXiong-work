from SM4_GCM import SM4_GCM_encrypt
from Optimized_SM4_GCM import Optilmized_SM4_GCM_encrypt
import secrets
from time import time

if __name__ == "__main__":
    # 生成2048字节随机字节串
    random_bytes = secrets.token_bytes(2048)  # 16字节 = 128比特

    # 转换为大整数（10进制或16进制）
    random_int = int.from_bytes(random_bytes, byteorder='big')  # 大端序转换
    P =random_int
   # P = 0x0123456789ABCDEFFEDCBA9876543210
    K = 0x0123456789ABCDEFFEDCBA9876543210
    IV = 0x0123456789ABCDEFFEDCBA9876543210



    # 测试时间
    Ptemp = P
    # 优化前
    t1 = time()
    for i in range(100):
        SM4_GCM_encrypt(K,P, IV,0)
    t2 = time()
    print("\n优化前进行1000次加密耗时:",t2 - t1, "秒")

    # 优化后
    t3 = time()
    for i in range(100):
        Optilmized_SM4_GCM_encrypt(K,Ptemp, IV,0)
    t4 = time()
    print("优化后进行1000次加密耗时:", t4 - t3, "秒")


