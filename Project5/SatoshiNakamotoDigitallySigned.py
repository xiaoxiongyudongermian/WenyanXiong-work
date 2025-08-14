from ecdsa import SigningKey, SECP256k1, numbertheory
import hashlib
import os


def sign_message(private_key: bytes, message: bytes) -> tuple:
    # 计算消息哈希
    e = int.from_bytes(hashlib.sha256(message).digest(), 'big')

    # 初始化曲线参数
    curve = SECP256k1
    n = curve.order
    d = int.from_bytes(private_key, 'big')

    # 生成随机k（实际应用中必须安全随机！）
    while True:
        k = int.from_bytes(os.urandom(32), 'big') % n
        if k == 0: continue

        # 计算 r = (k*G).x mod n
        kG = k * curve.generator
        r = kG.x() % n
        if r == 0: continue

        # 计算 s = k^(-1)(e + r*d) mod n
        k_inv = numbertheory.inverse_mod(k, n)
        s = (k_inv * (e + r * d)) % n
        if s == 0: continue

        return (r, s)


def verify_signature(public_key: bytes, message: bytes, signature: tuple) -> bool:
    r, s = signature
    curve = SECP256k1
    n = curve.order

    # 检查 r, s 范围
    if not (1 <= r < n and 1 <= s < n):
        return False

    # 计算消息哈希
    e = int.from_bytes(hashlib.sha256(message).digest(), 'big')

    # 计算 w = s^(-1) mod n
    w = numbertheory.inverse_mod(s, n)

    # 计算 u1, u2
    u1 = (e * w) % n
    u2 = (r * w) % n

    # 计算点 (x1, y1) = u1*G + u2*Q
    Q = vk.pubkey.point  # 从公钥解析点
    point = u1 * curve.generator + u2 * Q

    # 验证 r == x1 mod n
    return r == point.x() % n

if __name__ == "__main__":


    # 生成私钥（32字节随机数）
    private_key = os.urandom(32)

    # 从私钥生成ECDSA密钥对（secp256k1曲线）
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.get_verifying_key()

    print("私钥（16进制）:", sk.to_string().hex())
    print("公钥（未压缩）:", "04" + vk.to_string().hex())  # 04开头表示未压缩格式
    # 示例签名
    message = b"Hello, Bitcoin!"
    r, s = sign_message(private_key, message)
    print("签名 (r, s):", (hex(r)[2:], hex(s)[2:]))

    # 示例验证
    is_valid = verify_signature(vk.to_string(), message, (r, s))
    print("签名验证结果:", is_valid)