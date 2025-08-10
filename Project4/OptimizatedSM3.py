def padding(m):

    m = bin(int(m, 16))[2:].zfill(len(m) * 4)
    l = len(m)
    k = (448 - 1 - l) % 512
    if k < 0:
        k += 512
    strl = bin(l)[2:].zfill(64)
    pad = m + '1' + '0' * k + strl
    return l, k, pad


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
    # 进行优化
    W = [0]*68
    for i in range(16):
        W[i]=(Bi >> ((15 - i) * 32)) & 0xFFFFFFFF
    for i in range(16, 68):
        # 局部变量暂存依赖项，减少列表索引访问
        w_prev16 = W[i - 16]
        w_prev9 = W[i - 9]
        w_prev3 = W[i - 3]
        # 内联循环左移15位：circular_left_shift(w_prev3, 15)
        shift15_prev3 = ((w_prev3 << 15) | (w_prev3 >> 17)) & 0xFFFFFFFF  # 32-15=17
        term = w_prev16 ^ w_prev9 ^ shift15_prev3

        # 内联P1置换：P1(term) = term ^ 左移15 ^ 左移23
        p1_term = term ^ \
                  ((term << 15) | (term >> 17)) & 0xFFFFFFFF ^ \
                  ((term << 23) | (term >> 9)) & 0xFFFFFFFF  # 32-23=9

        # 内联循环左移7位：circular_left_shift(W[i-13], 7)
        w_prev13 = W[i - 13]
        shift7_prev13 = ((w_prev13 << 7) | (w_prev13 >> 25)) & 0xFFFFFFFF  # 32-7=25

        # 计算当前Wi并存储
        W[i] = (p1_term ^ shift7_prev13 ^ W[i - 6]) & 0xFFFFFFFF
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
        sum_ss1 = (rotA12 + E + rotTj) & 0xFFFFFFFF  # 关键：先模32位
        SS1 = circular_left_shift(sum_ss1, 7)

        SS2 = (SS1 ^ rotA12) & 0xFFFFFFFF

        TT1 = (FF(j, A, B, C) + D + SS2 + Wtemp[j]) & 0xFFFFFFFF
        TT2 = (GG(j, E, F, G) + H + SS1 + W[j]) & 0xFFFFFFFF

        D, C, B, A = C, circular_left_shift(B, 9), A, TT1
        H, G, F, E = G, circular_left_shift(F, 19), E, P0(TT2)


    new_V = [A ^ V[0], B ^ V[1], C ^ V[2], D ^ V[3], E ^ V[4], F ^ V[5], G ^ V[6], H ^ V[7]]
    Vi_plus_1 = 0
    for val in new_V:
        Vi_plus_1 = (Vi_plus_1 << 32) | val  # 按顺序左移组合，确保大端
    return Vi_plus_1


def SM3(m):
    IV = 0x7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e
    # 用02x确保每个字节转换为2位十六进制
    hex_str = ''.join(f"{ord(c):02x}" for c in m)
    l, k, padm = padding(hex_str)
    n = (l + k + 65) // 512  # 分组数
    B = [0] * n
    for i in range(n):
        group_bin = padm[i * 512: (i + 1) * 512]
        B[i] = int(group_bin, 2) if group_bin else 0

    Vi = IV
    for Bi in B:
        Vi = compression_function(Vi, Bi)
    return Vi


if __name__ == "__main__":
    m = 'abcd'*16
    if len(m) * 4 >= (1 << 64):
        print("输入长度l不满足l < 2^64")

    print(hex(SM3(m)))