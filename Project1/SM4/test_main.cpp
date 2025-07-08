#include <iostream>
#include <chrono>

using namespace std;
 
extern uint32_t* encrypt(uint32_t* X, uint32_t* MK);
extern uint32_t* decrypt(uint32_t* Y, uint32_t* MK);

extern uint32_t* Optimized_encrypt(uint32_t* X, uint32_t* MK);
extern uint32_t* Optimized_decrypt(uint32_t* X, uint32_t* MK);

extern void init_T_table();

int main()
{
	init_T_table();

	uint32_t* X = new uint32_t[4];
	uint32_t* MK = new uint32_t[4];
	X[0] = 0x01234567;
	X[1] = 0x89ABCDEF;
	X[2] = 0xFEDCBA98;
	X[3] = 0x76543210;
	
	MK[0] = X[0];
	MK[1] = X[1];
	MK[2] = X[2];
	MK[3] = X[3];

	uint32_t* Y = encrypt( X,  MK);
	uint32_t* Xtemp = decrypt(Y, MK);

	cout << "明文为";
	for (int i = 0; i < 4; i++)cout << hex << X[i];

	cout << "\n密钥为";
	for (int i = 0; i < 4; i++)cout << hex << MK[i];

	cout << "\n密文为";
	for (int i = 0; i < 4; i++)cout << hex << Y[i] ;

	cout << "\n解密后得到明文为";
	for (int i = 0; i < 4; i++)cout << hex << Xtemp[i] ;
	cout << endl;

	//测试时间
	for (int i = 0; i < 4; i++)Xtemp[i] = X[i];
	//优化前
	auto t1 = std::chrono::high_resolution_clock::now();
	for (int i = 0; i < 1000000; i++)
	{
		X = encrypt(X, MK);
	}
	auto t2 = std::chrono::high_resolution_clock::now();
	cout << "优化前进行1000000次加密后结果：";
	for (int i = 0; i < 4; i++)cout << hex << X[i];
	cout << "，耗时:" << dec << std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count() << " 微秒" << endl;


	//优化后
	auto t3 = std::chrono::high_resolution_clock::now();
	for (int i = 0; i < 1000000; i++)
	{
		Xtemp = Optimized_encrypt(Xtemp, MK);
	}
	auto t4 = std::chrono::high_resolution_clock::now();
	cout << "优化后进行1000000次加密后结果：";
	for (int i = 0; i < 4; i++)cout << hex << Xtemp[i];
	cout << "，耗时:" << dec << std::chrono::duration_cast<std::chrono::microseconds>(t4 - t3).count() << " 微秒" << endl;


	delete[] X;
	delete[] MK;
	delete[] Y;
	delete[] Xtemp;

	return 0;
}