# SM3算法

对长度为 $l(l<2^{64})$ 比特的消息 $m$ ，SM3杂凑算法经过填充和迭代压缩，生成杂凑值，杂凑值长度
为256比特。

## 常数与函数

### 初始值

$$IV=7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e$$

### 常量

$$
T_{j} = 
\begin{cases}
79cc4519 & 0 \leq j \leq 15 \\
7a879d8a & 16 \leq j \leq 63
\end{cases}
$$
### 布尔函数


$$
FF_{j}(X,Y,Z) = 
\begin{cases}
X \oplus Y \oplus Z & 0 \leq j \leq 15 \\
(X \wedge Y) \vee (X \wedge Z) \vee (Y \wedge Z) & 16 \leq j \leq 63
\end{cases}
$$

$$
GG_{j}(X,Y,Z) = 
\begin{cases}
X \oplus Y \oplus Z & 0 \leq j \leq 15 \\
(X \wedge Y) \vee (\neg X \wedge Z) & 16 \leq j \leq 63
\end{cases}
$$

其中 $X,Y,Z$ 为字。

### 置换函数

$$ P_{0}(X)=X\oplus (X<<<9)\oplus (X<<<17) $$

$$ P_{1}(X)=X\oplus (X<<<15)\oplus (X<<<23) $$

## 算法描述

### 填充

假设消息 $m$ 的长度为 $l$ 比特。首先将比特“1”添加到消息的末尾，再添加 $k$ 个“0”，$k$ 是满
足 $l+1+k≡ 448\ mod\ 512$ 的最小的非负整数。然后再添加一个64位比特串，该比特串是长度 $l$ 的二进制表示。填充后的消息 $m′$ 的比特长度为512的倍数。

### 迭代压缩

#### 迭代过程

将填充后的消息 $m'$ 按512比特进行分组： $m'=B^{(0)}B^{(1)}\cdots B^{(n-1)}$

$$ n = (l+k+65)/512 $$

对 $m'$ 按下列方式迭代：


$FOR\ i=0\ TO\ n-1$

$\qquad  V^{(i+1)} = CF(V^{(i)},B^{(i)})$

$ENDFOR$

其中 $CF$ 是压缩函数， $V^{(0)}$ 为256比特初始值 $IV$ ，  $B^{(i)}$ 为填充后的消息分组，迭代压缩的结果
为 $V^{(i)}$ 。


#### 消息扩展
将消息分组 $B^{(i)}$ 按以下方法扩展生成132个字 $W_{0},W_{1},\cdots ,W_{67},W_{0}',W_{1}',\cdots ,W_{63}'$ , 用于压缩函数 $CF$ ：

1. 将消息分组 $B^{(i)}$ 划分成16个字节 $W_{0},W_{1},\cdots ,W_{15}$

2. $FOR\ j=16\ TO\ 67$

$\qquad\qquad W_{j} \leftarrow P_{1}(W_{j−16} \oplus W_{j−9}  \oplus (W_{j−3}<<< 15)) \oplus(W_{j−13}<<< 7) \oplus W_{j−6}$

$\qquad ENDFOR$

4. $FOR\ j=0\ TO\ 63$
   
$\qquad\qquad W_{j}' = W_{j} \oplus W_{j+4}$

$\qquad ENDFOR$

#### 压缩函数

令 $A,B,C,D,E,F,G,H$ 为字寄存器, $SS1,SS2,TT1,TT2$ 为中间变量,压缩函数 $V^{i+1} = CF(V^{(i)},B^{(i)}), 0 \leq  i \leq n−1$ 。计算过程描述如下：




$ABCDEFGH \leftarrow V^{(i)}$

$FOR\ j=0\ TO\ 63$

$\qquad SS1 \leftarrow ((A<<<12)+E+(T_{j} <<< j))<<< 7$

$\qquad SS2 \leftarrow SS1\oplus (A<<<12)$

$\qquad TT1 \leftarrow FF_{j}(A,B,C)+D+SS2+W′_{j}$

$\qquad TT2 \leftarrow GG_{j}(E,F,G)+H +SS1+W_{j}$

$\qquad D\leftarrow C$

$\qquad C \leftarrow B<<<9$

$\qquad B \leftarrow A$

$\qquad A\leftarrow TT1$

$\qquad H \leftarrow G$

$\qquad G\leftarrow F <<<19$

$\qquad F \leftarrow E$

$\qquad E \leftarrow P_{0}(TT2)$

$ENDFOR$

$V^{(i+1)} \leftarrow  ABCDEFGH \oplus V^{(i)}$
 
 其中，字的存储为大端格式。

 ## 杂凑值
$ABCDEFGH \leftarrow V(n)$

输出256比特的杂凑值 $y=ABCDEFGH$ 。