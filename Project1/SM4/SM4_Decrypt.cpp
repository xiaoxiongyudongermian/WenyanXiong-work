#include <cstdint>
#include <iostream>

using namespace std;

extern uint32_t F(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t OptimizedF(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t* Gen_Round_Key(uint32_t* MK);

uint32_t* decrypt(uint32_t* Y, uint32_t* MK)
{
	//解密算法
	// 获取轮密钥
	uint32_t* rk = Gen_Round_Key(MK);
	//32次迭代
	uint32_t Ytemp[36];
	Ytemp[0] = Y[0];
	Ytemp[1] = Y[1];
	Ytemp[2] = Y[2];
	Ytemp[3] = Y[3];
	for (int i = 0; i < 32; i++)
	{
		Ytemp[i + 4] = F(Ytemp[i], Ytemp[i + 1], Ytemp[i + 2], Ytemp[i + 3], rk[31 - i]);
	}

	// 反序变换
	uint32_t* X = new uint32_t[4];
	X[0] = Ytemp[35];
	X[1] = Ytemp[34];
	X[2] = Ytemp[33];
	X[3] = Ytemp[32];
	
	delete[] rk;

	return X;
}


uint32_t* Optimized_decrypt(uint32_t* Y, uint32_t* MK)
{
	//优化后解密算法
	// 获取轮密钥
	uint32_t* rk = Gen_Round_Key(MK);
	//32次迭代
	uint32_t Ytemp[36];
	Ytemp[0] = Y[0];
	Ytemp[1] = Y[1];
	Ytemp[2] = Y[2];
	Ytemp[3] = Y[3];
	for (int i = 0; i < 32; i++)
	{
		Ytemp[i + 4] = OptimizedF(Ytemp[i], Ytemp[i + 1], Ytemp[i + 2], Ytemp[i + 3], rk[31 - i]);
	}

	// 反序变换
	uint32_t* X = new uint32_t[4];
	X[0] = Ytemp[35];
	X[1] = Ytemp[34];
	X[2] = Ytemp[33];
	X[3] = Ytemp[32];

	delete[] rk;

	return X;
}

extern uint32_t* decrypt(uint32_t* Y, uint32_t* MK);
uint32_t* Optimized_decrypt(uint32_t* Y, uint32_t* MK);