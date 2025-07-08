#include <iostream>

using namespace std;
 
extern uint32_t* encrypt(uint32_t* X, uint32_t* MK);
extern uint32_t* decrypt(uint32_t* Y, uint32_t* MK);
int main()
{
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


	for (int i = 0; i < 1000000; i++)
	{
		X = encrypt(X, MK);
	}
	for (int i = 0; i < 4; i++)cout << hex << X[i];
	cout << endl;

	delete[] X;
	delete[] MK;
	delete[] Y;
	delete[] Xtemp;

	return 0;
}