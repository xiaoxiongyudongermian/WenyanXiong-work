# 网络空间安全创新创业实践内容

## Project 1:

做SM4的软件实现和优化了 大家搞个git repo 在里面不断commit 代码以及配套的说明文档

## Project 2：

编程实现图片水印嵌入和提取（可依托开源项目二次开发），并进行鲁棒性测试，包括不限于翻转、平移、截取、调对比度等

## Project 3:

用circom实现poseidon2哈希算法的电路

### 要求： 

1. poseidon2哈希算法参数参考参考文档1的Table1，用(n,t,d)=(256,3,5)或(256,2,5)

2. 电路的公开输入用poseidon2哈希值，隐私输入为哈希原象，哈希算法的输入只考虑一个block即可。

3. 用Groth16算法生成证明

### 参考文档：

1. poseidon2哈希算法https://eprint.iacr.org/2023/323.pdf

2. circom说明文档https://docs.circom.io/

3. circom电路样例 https://github.com/iden3/circomlib
