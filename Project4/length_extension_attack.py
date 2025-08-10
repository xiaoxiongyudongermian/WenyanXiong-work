from SM3 import *

def length_extension_attack(original_hash, original_bit_length, extension_msg):
    # 1. 计算原始消息的填充（仅填充部分，不含原始消息）
    k = (448 - 1 - original_bit_length) % 512
    if k < 0:
        k += 512
    padding_bits = '1' + '0' * k + bin(original_bit_length)[2:].zfill(64)

    # 2. 原始哈希作为新的初始向量
    new_IV = original_hash

    # 3. 扩展消息的二进制（每个字符8位）
    ext_bin = ''.join(f"{ord(c):08b}" for c in extension_msg)
    # 总长度 = 原始消息长度 + 填充长度 + 扩展消息长度
    total_length = original_bit_length + len(padding_bits) + len(ext_bin)

    # 4. 计算扩展部分的填充（针对总长度）
    k_ext = (448 - 1 - total_length) % 512
    if k_ext < 0:
        k_ext += 512
    ext_padding = '1' + '0' * k_ext + bin(total_length)[2:].zfill(64)

    # 5. 扩展部分的完整分组（扩展消息 + 填充）
    ext_block_bits = ext_bin + ext_padding
    if len(ext_block_bits) % 512 != 0:
        raise ValueError("扩展块长度不是512的倍数")

    # 6. 用新IV迭代计算扩展部分的哈希
    Vi = new_IV
    for i in range(0, len(ext_block_bits), 512):
        block = ext_block_bits[i:i + 512]
        Bi = int(block, 2) if block else 0
        Vi = compression_function(Vi, Bi)
    return Vi


if __name__ == "__main__":
    original_msg = "abcd" * 16
    print(f"原始消息: {original_msg}")

    # 计算原始哈希
    original_hash = SM3(original_msg)
    print(f"原始哈希: {hex(original_hash)}")

    # 计算原始消息的比特长度（关键修正：用02x转换）
    hex_str = ''.join(f"{ord(c):02x}" for c in original_msg)
    original_bit_length, _, padm = padding(hex_str)
    print(f"原始消息比特长度: {original_bit_length}")

    # 扩展消息
    extension = "attack"
    print(f"扩展消息: {extension}")

    # 正常计算：M || padding(M) || extension 的哈希
    # 1. 构造 M || padding(M) 的二进制（padm）
    # 2. 构造扩展消息的二进制
    ext_bin = ''.join(f"{ord(c):08b}" for c in extension)
    # 3. 合并并填充得到完整消息的二进制
    full_bin = padm + ext_bin
    total_length = len(full_bin)
    k_full = (448 - 1 - total_length) % 512
    if k_full < 0:
        k_full += 512
    full_pad = full_bin + '1' + '0' * k_full + bin(total_length)[2:].zfill(64)
    # 4. 手动分组建模SM3计算（避免双重填充）
    n_full = len(full_pad) // 512
    B_full = [int(full_pad[i*512:(i+1)*512], 2) for i in range(n_full)]
    # 从初始IV计算完整哈希
    Vi_full = 0x7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e
    for Bi in B_full:
        Vi_full = compression_function(Vi_full, Bi)
    normal_hash = Vi_full
    print(f"正常计算的新哈希: {hex(normal_hash)}")

    # 攻击计算
    attack_hash = length_extension_attack(original_hash, original_bit_length, extension)
    print(f"攻击计算的新哈希: {hex(attack_hash)}")

    # 比较结果
    if normal_hash == attack_hash:
        print("✓ 攻击成功！SM3存在长度扩展漏洞")
    else:
        print("✗ 攻击失败")
