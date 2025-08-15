from ecdsa import SigningKey, SECP256k1, numbertheory
from phe import paillier
import random
import hashlib

def hash(x):
    # 哈希函数将U->G
    # 获取曲线参数
    curve = SECP256k1.curve
    G = SECP256k1.generator  # 生成元
    n = SECP256k1.order  # 群的阶
    # 计算哈希（SHA-256）
    h = hashlib.sha256(str(x).encode()).digest()
    h_int = int.from_bytes(h, 'big') % n

    # 计算 h_int * G（曲线上的点）
    point = h_int * G
    return point


def Round1(V,k1):
    #P1 执行
    # 计算哈希值
    Hv = [hash(v) for v in V]
    # 使用k1 对哈希值进行加密
    V_encrypted = [k1*hv for hv in Hv]
    # 打乱顺序
    random.shuffle(V_encrypted)
    return V_encrypted

def Round2(V_encrypted,W,k2,pk):
    # P2 执行
    # 二次加密
    Z = [k2*i for i in V_encrypted]
    # 计算哈希值 使用k1 对哈希值进行加，同态加密t
    W_encrypted = [(k2*hash(w),  pk.encrypt(t)) for w,t in W]
    # 打乱顺序
    random.shuffle(Z)
    random.shuffle(W_encrypted)
    return Z,W_encrypted

def Round3(Z,W_encrypted,k1,pk):
    # P1 执行
    # 求交集
    c1 = 0
    aencS = pk.encrypt(0)
    for hw, aenct in W_encrypted:
        if k1*hw in Z:
            c1 += 1
            aencS += aenct
    print("用户P1得到的c：",c1)
    return aencS

def Round4(aencs,sk):
    # P2 执行
    S = sk.decrypt(aencs)
    print("用户P2得到的S：",S)
    return S

if __name__=="__main__":
    # 参数
    V = {b"user1", b"user3", b"user5"}  # P1的用户集合
    W = {(b"user2", 100), (b"user3", 200), (b"user5", 300)}  # P2的(用户, 用户数据)集合
    # 初始化参数
    # 椭圆曲线群 secp256k1 的阶
    n = SECP256k1.order
    # P1的私钥k1
    k1 = random.randint(1, n-1)
    # P2的私钥k2 （pk,sk）
    k2 = random.randint(1, n-1)
    pk,sk= paillier.generate_paillier_keypair(n_length=2048)

    print("P1的用户集合：", V)
    print("P2的(用户, 用户数据)集合：", W)
    # 协议流程
    V_encrypted = Round1(V, k1)
    Z, W_encrypted = Round2(V_encrypted, W, k2, pk)
    aencs = Round3(Z, W_encrypted, k1, pk)
    S = Round4(aencs,sk)





