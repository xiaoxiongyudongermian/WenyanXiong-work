from Sbox import  Sbox

def Rotate_Left( x, d):
	# 将x循环左移d位
	return ((x << (d % 32)) | (x >> (32 - d % 32))) & 0xffffffff

def L( B):
	# C = L(B) = B ^ (B <<< 2) ^ (B <<< 10) ^ (B <<< 18) ^ (B <<< 24)
	C = B ^ (Rotate_Left(B, 2)) ^ (Rotate_Left(B, 10)) ^ (Rotate_Left(B, 18)) ^ (Rotate_Left(B, 24));
	return C

# 实现T函数
def T(A):
    '''
    合成置换T函数，T(A) = L(r(A))
    A = (a1, a2, a3, a4)
    B = r(A) = (Sbox(a1), Sbox(a2), Sbox(a3), Sbox(a4))
    '''
    a = [0]*4
    b = [0]*4
    for i in range(4):
        a[i] = (A >> (24 - 8 * i)) % 256
        b[i] = Sbox[a[i] >> 4][a[i] % 16]
    B = (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
    # C = L(B) = B ^ (B << < 2) ^ (B << < 10) ^ (B << < 18) ^ (B << < 24)
    return L(B)

def F(X0,X1,X2,X3,rk):
    # 轮函数F，F(X0, X1, X2, X3, rk) = X0 ^ T(X1 ^ X2 ^ X3 ^ rk)
    return X0 ^ T(X1 ^ X2 ^ X3 ^ rk)

# 利用查表优化
T_table0, T_table1, T_table2, T_table3 = [0]*256,[0]*256,[0]*256,[0]*256
for i in range(256):
    b = Sbox[i // 16][i % 16]
    T_table0[i] = L(b << 24)
    T_table1[i] = L(b << 16)
    T_table2[i] = L(b << 8)
    T_table3[i] = L(b)

# 优化后轮函数
def  OptimizedF( X0, X1,  X2,  X3,  rk):
    # 轮函数F，F(X0, X1, X2, X3, rk) = X0 ^ T_table(X1 ^ X2 ^ X3 ^ rk)
    A = X1 ^ X2 ^ X3 ^ rk
    return X0 ^ T_table0[(A >> 24) % 256] ^ T_table1[(A >> 16) % 256] ^ T_table2[(A >> 8) % 256] ^ T_table3[A % 256]

