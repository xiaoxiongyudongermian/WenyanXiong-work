#include <cstdint>

extern const uint8_t Sbox[16][16];
// 利用查表优化
uint32_t T_table0[256], T_table1[256], T_table2[256], T_table3[256];

uint32_t Rotate_Left(uint32_t x, int d)
{
	// 将x循环左移d位
	return (x << (d % 32)) | (x >> (32 - d % 32));
}

uint32_t L(uint32_t B)
{
	// C = L(B) = B ^ (B <<< 2) ^ (B <<< 10) ^ (B <<< 18) ^ (B <<< 24)
	uint32_t C = B ^ (Rotate_Left(B, 2)) ^ (Rotate_Left(B, 10)) ^ (Rotate_Left(B, 18)) ^ (Rotate_Left(B, 24));
	return C;
}

// 实现T函数
uint32_t T(uint32_t A)
{
	// 合成置换T函数，T(A) = L(r(A))
	
	// A = (a1,a2,a3,a4)
	// B = r(A) = (Sbox(a1),Sbox(a2),Sbox(a3),Sbox(a4))
	uint8_t a[4];
	uint8_t b[4];
	for (int i = 0; i < 4; i++)
	{
		a[i] = (A >> (24 - 8 * i)) % 256;
		b[i] = Sbox[a[i] >> 4][a[i] % 16];
	}
	uint32_t B = (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3];
	// C = L(B) = B ^ (B <<< 2) ^ (B <<< 10) ^ (B <<< 18) ^ (B <<< 24)
	return L(B);
}

uint32_t F(uint32_t X0, uint32_t X1, uint32_t X2, uint32_t X3, uint32_t rk)
{
	// 轮函数F，F(X0,X1,X2,X3,rk) = X0 ^ T(X1 ^ X2 ^ X3 ^ rk)
	return X0 ^ T(X1 ^ X2 ^ X3 ^ rk);
}



void init_T_table()
{
	for (int i = 0; i < 256; i++)
	{
		uint8_t b = Sbox[i / 16][i % 16];
		T_table0[i] = L(b << 24);
		T_table1[i] = L(b << 16);
		T_table2[i] = L(b << 8);
		T_table3[i] = L(b);
	}
	
}
//优化后轮函数
uint32_t OptimizedF(uint32_t X0, uint32_t X1, uint32_t X2, uint32_t X3, uint32_t rk)
{
	// 轮函数F，F(X0,X1,X2,X3,rk) = X0 ^ T_table(X1 ^ X2 ^ X3 ^ rk)
	uint32_t A = X1 ^ X2 ^ X3 ^ rk;

	return X0 ^ T_table0[(A >> 24) % 256] ^ T_table1[(A >> 16) % 256] ^ T_table2[(A >> 8) % 256] ^ T_table3[A % 256];
}

extern uint32_t F(uint32_t , uint32_t , uint32_t , uint32_t , uint32_t );
extern uint32_t Rotate_Left(uint32_t , int );
extern uint32_t OptimizedF(uint32_t X0, uint32_t X1, uint32_t X2, uint32_t X3, uint32_t rk);
extern void init_T_table();
