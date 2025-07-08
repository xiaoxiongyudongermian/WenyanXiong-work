#include <cstdint>

extern const uint8_t Sbox[16][16];
extern uint32_t Rotate_Left(uint32_t, int);

const uint32_t FK[4] = { 0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC };
const uint32_t CK[32] =
{   0x00070E15, 0x1C232A31, 0x383F464D, 0x545B6269,
    0x70777E85, 0x8C939AA1, 0xA8AFB6BD, 0xC4CBD2D9,
    0xE0E7EEF5, 0xFC030A11, 0x181F262D, 0x343B4249,
    0x50575E65, 0x6C737A81, 0x888F969D, 0xA4ABB2B9,
    0xC0C7CED5, 0xDCE3EAF1, 0xF8FF060D, 0x141B2229,
    0x30373E45, 0x4C535A61, 0x686F767D, 0x848B9299,
    0xA0A7AEB5, 0xBCC3CAD1, 0xD8DFE6ED, 0xF4FB0209,
    0x10171E25, 0x2C333A41, 0x484F565D, 0x646B7279 
};
uint32_t T2(uint32_t A)
{
	// 合成置换T'函数，T'(A) = L'(r(A))

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
	// C = L'(B) = B ^ (B <<< 13) ^ (B <<< 23) 
	uint32_t C = B ^ (Rotate_Left(B, 13)) ^ (Rotate_Left(B, 23));
	return C;
}

uint32_t* Gen_Round_Key(uint32_t* MK )
{
    uint32_t K[36];
    uint32_t* rk = new uint32_t[32];
	for (int i = 0; i < 4; i++)
	{
		K[i] = MK[i] ^ FK[i];
	}
    for (int i = 0; i < 32; i++)
    {
		K[i + 4] = K[i] ^ T2(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i]);
		rk[i] = K[i + 4];
    }
	return rk;
}

extern uint32_t* Gen_Round_Key(uint32_t* MK);




