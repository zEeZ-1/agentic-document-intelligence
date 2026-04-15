# Notes for Advanced Algebra and Its Applications*

## 1 Matrix Algebra

**Definition 1 (Linear operator).** Suppose $ X $ and $ Y $ are vector spaces. We say the operator $ A: X \to Y $ is a linear operator if  
$$
A(\alpha_1 x_1 + \alpha_2 x_2) = \alpha_1 A x_1 + \alpha_2 A x_2
$$  
for all $ \alpha_1, \alpha_2 \in \mathbb{R} $ and $ x_1, x_2 \in X $.

> **Note:** If $ X = \mathbb{R}^n $ and $ Y = \mathbb{R}^m $, any linear operator from $ X $ to $ Y $ can be represented as multiplication by an $ m \times n $ matrix.
>
> Second way to understand matrix is that all $ m $-by-$ n $ real matrix is a vector space which is denoted as $ \mathbb{R}^{m \times n} $.

**Notation:** Let $ A \in \mathbb{R}^{m \times n} $, then $ A $ can be represented as  
$$
A = 
\begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1} & a_{m2} & \cdots & a_{mn}
\end{bmatrix},\quad a_{ij} \in \mathbb{R}.
$$

**Example 2.**  
$$
A = \begin{bmatrix} 1 & 2 & 3 \\ -1 & 2 & 5 \end{bmatrix}
$$

**Definition 3 (Basic matrix operations).**

1.  **Transpose:** Let $ A \in \mathbb{R}^{m \times n} $ and $ C \in \mathbb{R}^{n \times m} $, $ C = A^\top \Rightarrow c_{ij} = a_{ji} $
2.  **Addition:** Let $ A, B, C \in \mathbb{R}^{m \times n} $, $ C = A + B \Rightarrow c_{ij} = a_{ij} + b_{ij} $
3.  **Scalar-matrix multiplication:** Let $ \alpha \in \mathbb{R} $ and $ A, C \in \mathbb{R}^{m \times n} $, $ C = \alpha A \Rightarrow c_{ij} = \alpha a_{ij} $
4.  **Matrix-vector product:** Let $ A \in \mathbb{R}^{m \times n} $ and $ v \in \mathbb{R}^n $, then $ Av \in \mathbb{R}^m $ is defined as $ [Av]_i = \sum_{j=1}^n a_{ij} v_j $
5.  **Matrix-matrix multiplication:** Let $ A \in \mathbb{R}^{m \times n} $, $ B \in \mathbb{R}^{n \times p} $, then $ C = AB \in \mathbb{R}^{m \times p} $, and  
    $$
    C = \begin{bmatrix} c_1 & c_2 & \cdots & c_p \end{bmatrix} := \begin{bmatrix} Ab_1 & Ab_2 & \cdots & Ab_p \end{bmatrix}
    $$

> **Remark 4.** There are multiple ways to compute matrix-matrix products; the choice depends on the specific application and context.

---
*(Page 1 End)*
<br>

**Definition 4 (Big-O Notation).**

*   **Definition:** Big-O describes the asymptotic growth rate of functions.
*   **Formal Definition:** For functions $ f(n), g(n) \geq 0 $, $ f(n) = O(g(n)) $ if and only if there exist constants $ C > 0 $ and $ n_0 $ such that for all $ n \geq n_0 $, $ f(n) \leq Cg(n) $.
*   **Intuition:** $ g(n) $ is an upper bound for $ f(n) $ (up to a constant factor) when $ n $ is sufficiently large.
*   **Examples:**
    *   $ 3n^2 + 5n + 2 = O(n^2) $
    *   $ \log(n^2) = O(\log n) $
    *   $ 2^n $ is not $ O(n^k) $ for any fixed $ k $
*   **Common Growth Rates:**  
    $ 1 < \log n < n < n \log n < n^2 < 2^n $

**Flops.** A flop is a floating point add, subtract, multiply, or divide. The number of flops in a given matrix computation is usually obtained by summing the amount of arithmetic associated with the most deeply nested statements.

**Table 1: Example of FLOP counts.**

| Operation | Dimension | FLOPs | FLOPs (O) |
| :--- | :--- | :--- | :--- |
| $ \alpha = x^\top y $ | $ x, y \in \mathbb{R}^n $ | $ 2n - 1 $ | $ \mathcal{O}(n) $ |
| $ y = y + \alpha x $ | $ x, y \in \mathbb{R}^n, \alpha \in \mathbb{R} $ | $ 2n $ | $ \mathcal{O}(n) $ |
| $ y = y + Ax $ | $ x \in \mathbb{R}^n, y \in \mathbb{R}^m, A \in \mathbb{R}^{m \times n} $ | $ 2mn $ | $ \mathcal{O}(mn) $ |
| $ C = C + AB $ | $ A \in \mathbb{R}^{m \times r}, B \in \mathbb{R}^{r \times n}, C \in \mathbb{R}^{m \times n} $ | $ 2mnr $ | $ \mathcal{O}(mnr) $ |

**Definition 5 (Block Matrix).**

Let $ A \in \mathbb{R}^{m \times n} $, then $ A $ can be partitioned into a block matrix with $ q $ rows and $ r $ columns:
$$
A = 
\begin{bmatrix}
A_{11} & A_{12} & \cdots & A_{1r} \\
A_{21} & A_{22} & \cdots & A_{2r} \\
\vdots & \vdots & \ddots & \vdots \\
A_{q1} & A_{q2} & \cdots & A_{qr}
\end{bmatrix}
$$

Where $ A_{ij} \in \mathbb{R}^{m_i \times n_j} $, satisfying:
$$
\sum_{j=1}^r n_j = n \quad \text{and} \quad \sum_{i=1}^q m_i = m.
$$

---
*(Page 2 End)*

<br>
<br>

---
<small>*Acknowledgments to Prof. Longxiu Huang at Michigan State University.</small>
<div style="text-align: right;">1</div>
<div style="text-align: right;">2</div>