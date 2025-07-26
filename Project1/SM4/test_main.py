from SM4_Decrypt import decrypt,Optimized_decrypt
from SM4_Encrypt import encrypt,Optimized_encrypt

from time import time


if __name__ == "__main__":
    X = 0x0123456789ABCDEFFEDCBA9876543210
    MK =  0x0123456789ABCDEFFEDCBA9876543210
    Y = encrypt(X, MK);
    Xtemp = decrypt(Y, MK)
    print("明文为",end=' ')

    print(hex(X)[2:],end='')

    print("\n密钥为",end=' ')
    print(hex(MK)[2:], end='')

    print("\n加密后得到的密文为", end=' ')
    print(hex(Y)[2:], end='')

    print("\n解密后得到的明文为", end=' ')
    print(hex(Xtemp)[2:], end='')

    # 测试时间
    Xtemp = X

    # 优化前
    t1 = time()
    for i in range(10000):
        X = encrypt(X, MK)
    t2 = time()
    print("\n优化前进行10000次加密后结果：",end='')
    print(hex(X)[2:],end='')
    print("，耗时:",t2-t1,"秒")

    # 优化后
    t3 = time()
    for i in range(10000):
        Xtemp = Optimized_encrypt(Xtemp, MK)
    t4 = time()
    print("优化后进行10000次加密后结果：", end='')
    print(hex(Xtemp)[2:], end='')
    print("，耗时:", t4 - t3, "秒")

