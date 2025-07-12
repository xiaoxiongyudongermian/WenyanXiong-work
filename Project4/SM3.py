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

    W = []
    for i in range(16):
        W.append((Bi >> ((15 - i) * 32)) & 0xFFFFFFFF)
    for i in range(16, 68):
        term = W[i - 16] ^ W[i - 9] ^ circular_left_shift(W[i - 3], 15)
        Wi = (P1(term) ^ circular_left_shift(W[i - 13], 7) ^ W[i - 6]) & 0xFFFFFFFF
        W.append(Wi)
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
    l, k, padm = padding(m)
    n = (l + k + 65) // 512
    B = []
    for i in range(n):
        group_bin = padm[i * 512: (i + 1) * 512]
        B.append(int(group_bin, 2))

    Vi = IV
    for Bi in B:
        Vi = compression_function(Vi, Bi)
    return hex(Vi)[2:].zfill(64).lower()


if __name__ == "__main__":
    m = '61626364'*16
    if len(m) * 4 >= (1 << 64):
        print("输入长度l不满足l < 2^64")

    print(SM3(m))