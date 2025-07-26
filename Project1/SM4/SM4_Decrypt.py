from function import F,OptimizedF
from Key_Expansion_Algorithm import Gen_Round_Key


def decrypt(Y,MK):
    # 解密算法
    # 获取轮密钥
    rk = Gen_Round_Key(MK)
    # 32次迭代
    Ytemp = [0] * 36
    temp = Y
    for i in range(4):
        Ytemp[3 - i] = temp & 0xffffffff
        temp = temp >> 32

    for i in range(32):
        Ytemp[i + 4] = F(Ytemp[i], Ytemp[i + 1], Ytemp[i + 2], Ytemp[i + 3], rk[31 - i])
    # 反序变换
    result = 0
    for i in range(4):
        result = result << 32
        result += Ytemp[35 - i]

    return result
def Optimized_decrypt(Y,MK):
    # 解密算法
    # 获取轮密钥
    rk = Gen_Round_Key(MK)
    # 32次迭代
    Ytemp = [0] * 36
    temp = Y
    for i in range(4):
        Ytemp[3 - i] = temp & 0xffffffff
        temp = temp >> 32

    for i in range(32):
        Ytemp[i + 4] = OptimizedF(Ytemp[i], Ytemp[i + 1], Ytemp[i + 2], Ytemp[i + 3], rk[31 - i])
    # 反序变换
    result = 0
    for i in range(4):
        result = result << 32
        result += Xtemp[35 - i]

    return result