from function import F,OptimizedF
from Key_Expansion_Algorithm import Gen_Round_Key


def encrypt(X,MK):
    # 解密算法
    # 获取轮密钥
    rk = Gen_Round_Key(MK)

    # 32次迭代
    Xtemp = [0] * 36

    temp = X
    for i in range(4):
        Xtemp[3-i] = temp & 0xffffffff
        temp = temp >> 32

    for i in range(32):
        Xtemp[i + 4] = F(Xtemp[i], Xtemp[i + 1], Xtemp[i + 2], Xtemp[i + 3], rk[i])
    # 反序变换
    result = 0
    for i in range(4):
        result = result << 32
        result += Xtemp[35-i]

    return result

def Optimized_encrypt(X,MK):
    # 解密算法
    # 获取轮密钥
    rk = Gen_Round_Key(MK)
    # 32次迭代
    Xtemp = [0] * 36
    temp = X
    for i in range(4):
        Xtemp[3 - i] = temp & 0xffffffff
        temp = temp >> 32

    for i in range(32):
        Xtemp[i + 4] = OptimizedF(Xtemp[i], Xtemp[i + 1], Xtemp[i + 2], Xtemp[i + 3], rk[i])
    # 反序变换
    result = 0
    for i in range(4):
        result = result << 32
        result += Xtemp[35 - i]

    return result