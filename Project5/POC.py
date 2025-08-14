from gmssl import sm2, func
from ecdsa import SigningKey, NIST256p, numbertheory
import binascii
import hashlib

# 生成密钥对
private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'


# 1.泄露随机数k导致私钥泄露
def leak_k_poc():
    print("\n=== 1.泄露随机数k导致私钥泄露 ===")
    # 原始消息
    message = b"test message for k leakage"

    # 生成签名（使用固定k，模拟k泄露）
    k = "123456789ABCDEF0123456789ABCDEF123456789ABCDEF0123456789ABCDEF"  # 泄露的k

    # 创建SM2对象
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
    # 使用指定k签名
    sign = sm2_crypt.sign(message, k)

    r = int(sign[:64], 16)  # 前64字符是r
    s = int(sign[64:], 16)  # 后64字符是s

    # 攻击者推导私钥（基于SM2签名公式）
    # 公式：d = (k - s) * inv(s + r) mod n

    #标准的 SM2 曲线参数 n
    n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123


    numerator = (int(k, 16) - s) % n
    denominator = pow((s+r)%n, -1, n)
    d_leaked = (numerator * denominator) % n

    # 验证推导结果
    original_d = int(private_key, 16)
    assert d_leaked == original_d, "验证失败"
    print(f"推导私钥成功：\n原始私钥: {private_key}\n推导私钥: {hex(d_leaked)[2:].upper().zfill(64)}")


# 2.重用随机数k导致私钥泄露
def reuse_k_poc():
    print("\n=== 2.重用随机数k导致私钥泄露 ===")
    # 两条不同消息
    message1 = b"message 1 with reused k"
    message2 = b"message 2 with reused k"

    # 创建SM2对象
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)

    # 重用k生成两个签名
    k = "123456789ABCDEF0123456789ABCDEF123456789ABCDEF0123456789ABCDEF"
    sign1 = sm2_crypt.sign(message1, k)
    sign2 = sm2_crypt.sign(message2, k)

    # 解析签名
    r1 = int(sign1[:64], 16)
    s1 = int(sign1[64:], 16)
    r2 = int(sign2[:64], 16)
    s2 = int(sign2[64:], 16)

    # 攻击者推导私钥（基于两个签名的关系）
    # 公式：d = (s2 - s1) * inv(s1 - s2 + r1 - r2) mod n
    # 标准的 SM2 曲线参数 n
    n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123

    numerator = (s2 - s1) % n
    denominator = (s1 - s2 + r1 - r2) % n
    d_leaked = (numerator * pow(denominator, -1, n)) % n

    # 验证
    original_d = int(private_key, 16)
    assert d_leaked == original_d, "验证失败"
    print(f"推导私钥成功：\n原始私钥: {private_key}\n推导私钥: {hex(d_leaked)[2:].upper().zfill(64)}")


# 3.不同用户重用k导致互相泄露私钥
def cross_user_reuse_k_poc():
    print("\n=== 3.不同用户重用k导致互相泄露私钥 ===")
    # 生成两个用户的密钥对
    # 生成随机私钥（32字节，64字符）
    user1_pri = func.random_hex(64)

    # 使用ecdsa计算公钥（SM2使用NIST P-256曲线）
    sk1 = SigningKey.from_string(bytes.fromhex(user1_pri), curve=NIST256p)
    vk1 = sk1.get_verifying_key()
    user1_pub = "04" + vk1.to_string().hex()  # SM2公钥格式：04 + x + y

    # 初始化SM2
    user1 = sm2.CryptSM2(public_key=user1_pub, private_key=user1_pri)


    user2_pri = func.random_hex(64)
    # 使用ecdsa计算公钥（SM2使用NIST P-256曲线）
    sk2 = SigningKey.from_string(bytes.fromhex(user1_pri), curve=NIST256p)
    vk2 = sk2.get_verifying_key()
    user2_pub = "04" + vk2.to_string().hex()  # SM2公钥格式：04 + x + y
    # 初始化SM2
    user2 = sm2.CryptSM2(public_key=user2_pub, private_key=user2_pri)

    # 两条消息
    msg1 = b"user1's message"
    msg2 = b"user2's message"

    # 重用k生成签名
    k = "123456789ABCDEF0123456789ABCDEF123456789ABCDEF0123456789ABCDEF"
    sign1 = user1.sign(msg1, k)
    sign2 = user2.sign(msg2, k)

    # 解析签名
    r1 = int(sign1[:64], 16)
    s1 = int(sign1[64:], 16)
    r2 = int(sign2[:64], 16)
    s2 = int(sign2[64:], 16)

    # 互相推导私钥
    # 标准的 SM2 曲线参数 n
    n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123

    d1_leaked = ((int(k, 16) - s1) * pow((s1+r1), -1, n)) % n
    d2_leaked = ((int(k, 16) - s2) * pow((s2+r2), -1, n)) % n

    # 验证
    assert d1_leaked == int(user1_pri, 16) and d2_leaked == int(user2_pri, 16), "验证失败"
    print(f"用户1私钥推导成功: {hex(d1_leaked)[2:].upper().zfill(64)}")
    print(f"用户2私钥推导成功: {hex(d2_leaked)[2:].upper().zfill(64)}")


# 4.SM2与ECDSA共用d和k导致私钥泄露
def shared_dk_poc():
    print("\n=== 4.SM2与ECDSA共用d和k导致私钥泄露 ===")
    # 共用私钥d
    shared_d = func.random_hex(64)
    # 转换为字节
    d_bytes = binascii.unhexlify(shared_d)

    # 计算公钥
    sk = SigningKey.from_string(d_bytes, curve=NIST256p)
    vk = sk.get_verifying_key()
    shared_pub = "04" + vk.to_string().hex()  # SM2格式
    sm2_shared = sm2.CryptSM2(public_key=shared_pub, private_key=shared_d)


    # 共用消息和随机数k
    message = b"shared message for sm2 and ecdsa"
    k = "123456789ABCDEF0123456789ABCDEF123456789ABCDEF0123456789ABCDEF"

    # 生成SM2签名
    sm2_sign = sm2_shared.sign(message, k)
    r2 = int(sm2_sign[:64], 16)
    s2 = int(sm2_sign[64:], 16)

    # 标准的 SM2 曲线参数 n
    n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123

    # 生成ECDSA签名（使用相同d和k）
    # ECDSA签名公式：s = k^-1*(e + r*d) mod n
    e = int(hashlib.sha256(message).hexdigest(), 16) % n # 哈希消息

    # 计算 r1 = (k*G).x mod n
    kG = int(k, 16) * NIST256p.generator  # k*G
    r1 = kG.x() % n  # ECDSA的r
    # 计算 s1 = k^(-1) * (e + r*d) mod n
    k_inv = numbertheory.inverse_mod(int(k, 16), n)
    d_int = int(shared_d, 16)
    s1 = (k_inv * (e + r1 * d_int)) % n  # ECDSA的s

    # 推导私钥d
    # 公式：d = (s1*s2 - e) * inv(r1 - s1*s2 - s1*r2) mod n
    numerator = (s1 * s2 - e) % n
    denominator = (r1 - s1 * s2 - s1 * r2) % n
    d_leaked = (numerator * pow(denominator,-1,n)) % n

    # 验证
    assert d_leaked == int(shared_d, 16), "场景4验证失败"
    print(f"推导私钥成功：\n原始私钥: {shared_d.upper()}\n推导私钥: {hex(d_leaked)[2:].upper().zfill(64)}")



if __name__ == "__main__":


    leak_k_poc()
    reuse_k_poc()
    cross_user_reuse_k_poc()
    shared_dk_poc()