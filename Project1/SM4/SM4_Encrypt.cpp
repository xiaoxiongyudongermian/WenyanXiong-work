#include <cstdint>
#include <iostream>

using namespace std;

extern uint32_t F(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t OptimizedF(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t* Gen_Round_Key(uint32_t* MK);

uint32_t* encrypt(uint32_t* X, uint32_t* MK)
{
	//加密算法
	// 获取轮密钥
	uint32_t* rk = Gen_Round_Key(MK);
	//32次迭代
	uint32_t Xtemp[36];
	Xtemp[0] = X[0];
	Xtemp[1] = X[1];
	Xtemp[2] = X[2];
	Xtemp[3] = X[3];
	for(int i = 0; i < 32; i++)
	{ 
		Xtemp[i + 4] = F(Xtemp[i], Xtemp[i + 1], Xtemp[i + 2], Xtemp[i + 3], rk[i]);
	}

	// 反序变换
	uint32_t* Y = new uint32_t[4];
	Y[0] = Xtemp[35];
	Y[1] = Xtemp[34];
	Y[2] = Xtemp[33];
	Y[3] = Xtemp[32];
	
	delete[] rk;

	return Y;
}

//优化后
uint32_t* Optimized_encrypt(uint32_t* X, uint32_t* MK)
{
	//加密算法
	// 获取轮密钥
	uint32_t* rk = Gen_Round_Key(MK);
	//32次迭代
	uint32_t Xtemp[36];
	Xtemp[0] = X[0];
	Xtemp[1] = X[1];
	Xtemp[2] = X[2];
	Xtemp[3] = X[3];
	for (int i = 0; i < 32; i++)
	{
		Xtemp[i + 4] = OptimizedF(Xtemp[i], Xtemp[i + 1], Xtemp[i + 2], Xtemp[i + 3], rk[i]);
	}

	// 反序变换
	uint32_t* Y = new uint32_t[4];
	Y[0] = Xtemp[35];
	Y[1] = Xtemp[34];
	Y[2] = Xtemp[33];
	Y[3] = Xtemp[32];

	delete[] rk;

	return Y;
}

extern uint32_t* encrypt(uint32_t* X, uint32_t* MK);
uint32_t* Optimized_encrypt(uint32_t* X, uint32_t* MK);