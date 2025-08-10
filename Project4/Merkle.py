def circular_left_shift(num, d, bit_length=32):
    d %= bit_length
    return ((num << d) | (num >> (bit_length - d))) & 0xFFFFFFFF


def P0(X):
    return (X ^ circular_left_shift(X, 9) ^ circular_left_shift(X, 17)) & 0xFFFFFFFF


def P1(X):
    return (X ^ circular_left_shift(X, 15) ^ circular_left_shift(X, 23)) & 0xFFFFFFFF


def FF(j, X, Y, Z):
    if 0 <= j <= 15:
        return (X ^ Y ^ Z) & 0xFFFFFFFF
    elif 16 <= j <= 63:
        return ((X & Y) | (X & Z) | (Y & Z)) & 0xFFFFFFFF
    return 0


def GG(j, X, Y, Z):
    if 0 <= j <= 15:
        return (X ^ Y ^ Z) & 0xFFFFFFFF
    elif 16 <= j <= 63:
        return ((X & Y) | ((~X) & Z)) & 0xFFFFFFFF
    return 0


def message_extension(Bi):
    W = [0] * 68
    for i in range(16):
        W[i] = (Bi >> ((15 - i) * 32)) & 0xFFFFFFFF
    for i in range(16, 68):
        term = W[i - 16] ^ W[i - 9] ^ circular_left_shift(W[i - 3], 15)
        Wi = (P1(term) ^ circular_left_shift(W[i - 13], 7) ^ W[i - 6]) & 0xFFFFFFFF
        W[i] = Wi
    Wtemp = [W[i] ^ W[i + 4] for i in range(64)]
    return W, Wtemp


def compression_function(Vi, Bi):
    W, Wtemp = message_extension(Bi)
    V = [(Vi >> ((7 - j) * 32)) & 0xFFFFFFFF for j in range(8)]
    A, B, C, D, E, F, G, H = V

    for j in range(64):
        Tj = 0x79cc4519 if j <= 15 else 0x7a879d8a
        rotA12 = circular_left_shift(A, 12)
        rotTj = circular_left_shift(Tj, j % 32)
        sum_ss1 = (rotA12 + E + rotTj) & 0xFFFFFFFF
        SS1 = circular_left_shift(sum_ss1, 7)
        SS2 = (SS1 ^ rotA12) & 0xFFFFFFFF
        TT1 = (FF(j, A, B, C) + D + SS2 + Wtemp[j]) & 0xFFFFFFFF
        TT2 = (GG(j, E, F, G) + H + SS1 + W[j]) & 0xFFFFFFFF

        D, C, B, A = C, circular_left_shift(B, 9), A, TT1
        H, G, F, E = G, circular_left_shift(F, 19), E, P0(TT2)

    new_V = [A ^ V[0], B ^ V[1], C ^ V[2], D ^ V[3], E ^ V[4], F ^ V[5], G ^ V[6], H ^ V[7]]
    Vi_plus_1 = 0
    for val in new_V:
        Vi_plus_1 = (Vi_plus_1 << 32) | val
    return Vi_plus_1


def sm3_hash(data: bytes) -> bytes:
    """使用用户提供的SM3实现计算哈希（输入为字节，输出为字节）"""
    hex_str = data.hex()
    IV = 0x7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e
    l, k, padm = padding(hex_str)
    n = (l + k + 65) // 512
    B = [0] * n
    for i in range(n):
        group_bin = padm[i * 512: (i + 1) * 512]
        B[i] = int(group_bin, 2) if group_bin else 0
    Vi = IV
    for Bi in B:
        Vi = compression_function(Vi, Bi)
    return Vi.to_bytes(32, byteorder='big')


def padding(m):
    m_bin = bin(int(m, 16))[2:].zfill(len(m) * 4)
    l = len(m_bin)
    k = (448 - 1 - l) % 512
    if k < 0:
        k += 512
    strl = bin(l)[2:].zfill(64)
    pad = m_bin + '1' + '0' * k + strl
    return l, k, pad


from typing import List, Tuple, Optional, Dict


class MerkleTree:
    def __init__(self, leaves: List[bytes]):
        self.leaves = leaves
        self.leaf_count = len(leaves)
        self.nodes: Dict[int, List[bytes]] = {}  # 存储各层节点哈希（字节形式）
        self.root = self.build_tree()

    def build_tree(self) -> bytes:
        """构建Merkle树，叶子节点前缀0x00，内部节点前缀0x01"""
        current_level = [sm3_hash(b'\x00' + leaf) for leaf in self.leaves]
        level = 0
        self.nodes[level] = current_level

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if (i + 1) < len(current_level) else left
                combined = b'\x01' + left + right
                next_level.append(sm3_hash(combined))
            level += 1
            self.nodes[level] = next_level
            current_level = next_level

        return current_level[0] if current_level else b''

    def get_leaf_hash(self, index: int) -> Optional[bytes]:
        if 0 <= index < self.leaf_count:
            return self.nodes[0][index]
        return None

    def generate_inclusion_proof(self, index: int) -> Tuple[List[bytes], List[bool]]:
        """生成存在性证明：(兄弟哈希列表, 兄弟是否在左)"""
        if index < 0 or index >= self.leaf_count:
            return [], []

        proof = []
        directions = []  # True: 兄弟在左；False: 兄弟在右
        current_index = index
        current_level = 0

        while current_level in self.nodes and len(self.nodes[current_level]) > 1:
            is_right = current_index % 2 == 1
            sibling_index = current_index - 1 if is_right else current_index + 1

            if sibling_index >= len(self.nodes[current_level]):
                sibling_index = current_index

            proof.append(self.nodes[current_level][sibling_index])
            directions.append(is_right)

            current_index = current_index // 2
            current_level += 1

        return proof, directions

    @staticmethod
    def verify_inclusion(
            root: bytes,
            leaf_hash: bytes,
            index: int,
            proof: List[bytes],
            directions: List[bool]
    ) -> bool:
        """验证存在性证明"""
        if len(proof) != len(directions):
            return False

        current_hash = leaf_hash
        for i in range(len(proof)):
            sibling_hash = proof[i]
            if directions[i]:
                combined = b'\x01' + sibling_hash + current_hash
            else:
                combined = b'\x01' + current_hash + sibling_hash
            current_hash = sm3_hash(combined)

        return current_hash == root

    def generate_exclusion_proof(self, index: int) -> Tuple[
        Optional[bytes], Optional[int], Optional[bytes], Optional[int], List[bytes], List[bool], List[bytes], List[bool]]:
        """生成不存在性证明：修正邻居寻找逻辑"""
        # 若索引在叶子范围内（存在），返回无效证明
        if 0 <= index < self.leaf_count:
            return None, None, None, None, [], [], [], []

        # 寻找左邻居（小于index的最大存在索引，存在索引为0到leaf_count-1）
        left_index = None
        if index > 0:
            candidate = index - 1
            if candidate < self.leaf_count:
                left_index = candidate  # 候选在范围内，直接作为左邻居
            else:
                # 候选超出范围，左邻居为最后一个叶子
                left_index = self.leaf_count - 1 if self.leaf_count > 0 else None

        # 寻找右邻居（大于index的最小存在索引，存在索引为0到leaf_count-1）
        right_index = None
        if index < self.leaf_count - 1:
            candidate = index + 1
            if candidate < self.leaf_count:
                right_index = candidate  # 候选在范围内，直接作为右邻居

        # 获取左邻居的证明
        left_hash = self.get_leaf_hash(left_index) if left_index is not None else None
        left_proof, left_dirs = self.generate_inclusion_proof(left_index) if left_index is not None else ([], [])

        # 获取右邻居的证明
        right_hash = self.get_leaf_hash(right_index) if right_index is not None else None
        right_proof, right_dirs = self.generate_inclusion_proof(right_index) if right_index is not None else ([], [])

        return left_hash, left_index, right_hash, right_index, left_proof, left_dirs, right_proof, right_dirs

    @staticmethod
    def verify_exclusion(
            root: bytes,
            index: int,
            left_hash: Optional[bytes],
            left_index: Optional[int],
            right_hash: Optional[bytes],
            right_index: Optional[int],
            left_proof: List[bytes],
            left_dirs: List[bool],
            right_proof: List[bytes],
            right_dirs: List[bool],
            leaf_count: int
    ) -> bool:
        """验证不存在性证明"""
        # 验证左邻居存在且小于index
        if left_index is not None and left_hash is not None:
            if left_index >= index:
                return False
            if not MerkleTree.verify_inclusion(root, left_hash, left_index, left_proof, left_dirs):
                return False

        # 验证右邻居存在且大于index
        if right_index is not None and right_hash is not None:
            if right_index <= index:
                return False
            if not MerkleTree.verify_inclusion(root, right_hash, right_index, right_proof, right_dirs):
                return False

        # 验证左右邻居相邻（仅当两者都存在时）
        if left_index is not None and right_index is not None:
            if left_index + 1 != right_index:
                return False

        # 边界情况处理：
        # 1. 无左邻居 → index必须为0（最小可能索引）
        if left_index is None and index != 0:
            return False
        # 2. 无右邻居 → index必须≥leaf_count-1（最大可能索引）
        if right_index is None and index < leaf_count - 1:
            return False

        return True


# 测试代码
def test_merkle_tree():
    import random
    import string

    print("生成10万个叶子节点...")
    leaf_count = 100000
    leaves = [''.join(random.choices(string.ascii_letters, k=16)).encode() for _ in range(leaf_count)]

    print("构建Merkle树...")
    merkle_tree = MerkleTree(leaves)
    print(f"根哈希: {merkle_tree.root.hex()}")

    # 测试存在性证明
    test_index = 12345
    print(f"\n测试存在性证明（索引: {test_index}）")
    leaf_hash = merkle_tree.get_leaf_hash(test_index)
    proof, directions = merkle_tree.generate_inclusion_proof(test_index)
    inclusion_result = MerkleTree.verify_inclusion(
        merkle_tree.root, leaf_hash, test_index, proof, directions
    )
    print(f"存在性证明验证结果: {'成功' if inclusion_result else '失败'}")

    # 测试不存在性证明（超出范围的索引）
    non_existent_index = leaf_count + 100  # 100100
    print(f"\n测试不存在性证明（索引: {non_existent_index}）")
    left_hash, left_idx, right_hash, right_idx, lp, ld, rp, rd = merkle_tree.generate_exclusion_proof(non_existent_index)
    exclusion_result = MerkleTree.verify_exclusion(
        merkle_tree.root, non_existent_index,
        left_hash, left_idx, right_hash, right_idx,
        lp, ld, rp, rd,
        leaf_count
    )
    print(f"不存在性证明验证结果: {'成功' if exclusion_result else '失败'}")

    # 测试不存在性证明（远大于叶子范围的索引）
    non_existent_index = 500000
    print(f"\n测试不存在性证明（索引: {non_existent_index}）")
    left_hash, left_idx, right_hash, right_idx, lp, ld, rp, rd = merkle_tree.generate_exclusion_proof(non_existent_index)
    exclusion_result = MerkleTree.verify_exclusion(
        merkle_tree.root, non_existent_index,
        left_hash, left_idx, right_hash, right_idx,
        lp, ld, rp, rd,
        leaf_count
    )
    print(f"不存在性证明验证结果: {'成功' if exclusion_result else '失败'}")


if __name__ == "__main__":
    test_merkle_tree()
