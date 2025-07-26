from SM4_Encrypt import encrypt
from SM4_GCM import SM4_GCM_encrypt

from time import time

def gf_multiply(a, b):
    """在有限域GF(2^128)上执行a*b mod P(x)，其中P(x) = x^128 + x^7 + x^2 + x + 1"""
    p = 0x80000000000000000000000000000087
    result = 0

    for i in range(128):
        if b & 1:
            result ^= a
        a <<= 1
        if a & (1 << 128):
            a ^= p
        b >>= 1

    return result

def precompute_gf_mult_table(h):
    """预计算h的256个倍数表（每个128位）"""
    table = [0] * 256  # 初始化表

    for byte_val in range(256):
        # 构造值：byte_val << 120（即byte_val在最高字节的位置）
        value = (byte_val << 120) & ((1 << 128) - 1)

        # 计算h × value（使用原始GF乘法）
        product = gf_multiply(h, value)

        # 存入表中
        table[byte_val] = product

    return table

def Optilmized_gf_multiply(a,table):
    """使用预计算表优化GF(2^128)乘法"""
    result = 0

    # 将a按字节分解处理
    for i in range(16):  # 128位 = 16字节
        # 提取当前字节（从最高字节开始）
        byte_val = (a >> ((15 - i) * 8)) & 0xFF

        # 查表获取h × (byte_val << (i*8))
        # 注意：表中存储的是h × (byte_val << 120)，需右移调整位置
        shifted_product = table[byte_val] >> ((15 - i) * 8)

        # 异或到结果中
        result ^= shifted_product

    return result




def split_int_to_blocks(value, block_size=128):
    """将大整数按指定块大小分块"""
    if value == 0:
        return [0]  # 处理零值

    # 计算需要的块数
    bit_length = value.bit_length()
    n_blocks = (bit_length + block_size - 1) // block_size

    blocks = []
    mask = (1 << block_size) - 1  # 用于提取每块的掩码

    for i in range(n_blocks):
        # 提取当前块的值（从低位到高位处理）
        block = (value >> (i * block_size)) & mask
        blocks.append(block)

    # 反转以保持与原始字节序一致（从高位到低位）
    return blocks[::-1]


def ghash(h, aad, ciphertext):
    # 实现GHASH函数（输入全为大整数）

    # 分块处理AAD和密文
    aad_blocks = split_int_to_blocks(aad)
    ciphertext_blocks = split_int_to_blocks(ciphertext)

    # 计算AAD和密文的比特长度
    len_aad_bits = aad.bit_length() if aad > 0 else 0
    len_cipher_bits = ciphertext.bit_length() if ciphertext > 0 else 0

    # 创建长度块 [len(AAD) || len(C)] (各64位)
    len_block = (len_aad_bits << 64) | len_cipher_bits

    # 初始化Y为0
    y = 0
    table = precompute_gf_mult_table(h)
    # 处理AAD块
    for block in aad_blocks:
        y ^= block
        y = Optilmized_gf_multiply(y, table)

    # 处理密文块
    for block in ciphertext_blocks:
        y ^= block
        y = Optilmized_gf_multiply(y, table)

    # 处理长度块
    y ^= len_block
    y = Optilmized_gf_multiply(y, table)

    return y  # 返回大整数结果

def Optilmized_SM4_GCM_encrypt(K,P,IV,add=0):
    # 加密，最终返回密文及标签

    # 查看p为多少bit，并且进行分组
    n = len(bin(P)[2:]) // 128
    temp = P
    ptemp = [0] * n
    for i in range(n):
        ptemp[i] = temp & 0xffffffffffffffffffffffffffffffff
        temp = temp >> 128
    if temp != 0:
        n += 1
        ptemp.append(temp)
    ptemp = ptemp[::-1]


    # 生成哈希值
    h = encrypt(0,K)
    # 生成初始计数器j0
    j0 = (IV << 32 | 0x00000001) & 0xffffffffffffffffffffffffffffffff

    # CTR模式加密
    C = ''
    for i in range(n):
        s = encrypt(j0+1+i,K)
        ctemp =  ptemp[i] ^ s
        C = C + hex(ctemp)[2:]

    C = eval('0x'+C)
    # GHASH
    y = ghash(h,add,C)

    T = encrypt(j0,K) ^ y

    return (C,T)

def Optilmized_SM4_GCM_decrypt(K,C,IV,T,add=0):
    # 加密，最终返回密文及标签


    # 查看c为多少bit，并且进行分组
    n = len(bin(C)[2:]) // 128
    temp = C
    ctemp = [0] * n
    for i in range(n):
        ctemp[i] = temp & 0xffffffffffffffffffffffffffffffff
        temp = temp >> 128
    if temp != 0:
        n += 1
        ctemp.append(temp)
    ctemp = ctemp[::-1]


    # 生成哈希值
    h = encrypt(0,K)
    # 生成初始计数器j0
    j0 = (IV << 32 | 0x00000001) & 0xffffffffffffffffffffffffffffffff



    # GHASH
    y = ghash(h,add,C)

    T2 = encrypt(j0,K) ^ y

    if T2 != T:
        #拒绝解密

        return 'None'

    # CTR模式解密
    P = ''

    for i in range(n):
        s = encrypt(j0+1+i, K)
        ptemp = ctemp[i] ^ s
        P = P + hex(ptemp)[2:]
    P = eval('0x'+P)
    return P





if __name__ == "__main__":
    P = 0x0123456789ABCDEFFEDCBA9876543210
    K = 0x0123456789ABCDEFFEDCBA9876543210
    IV = 0x0123456789ABCDEFFEDCBA9876543210
    C, T = Optilmized_SM4_GCM_encrypt(K,P, IV,0)
    P2 = Optilmized_SM4_GCM_decrypt(K, C, IV, T,0)

    print("明文P=",(hex(P)[2:]))
    print("SM4-GCM加密结果,(C,T)=",(hex(C)[2:],hex(T)[2:]))
    print("SM4-GCM解密结果,P=",hex(P2)[2:])
