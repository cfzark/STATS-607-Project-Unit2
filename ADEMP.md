# ADEMP: Lasso Support Recovery

## Aims

Reproduce Figures 1 and 2 of Wainwright (2009): the transition in Lasso's probability of exact signed support recovery under independent Gaussian designs. Examine whether curves for different dimensions align after rescaling sample size and whether the transition becomes sharper as dimension increases. The paper reports a transition near the theoretical threshold of 1 on this scale.

## Data-generating mechanisms

Generate independent replicates from

$$
y=X\beta^*+\varepsilon,\qquad X_{ij}\overset{\mathrm{iid}}{\sim}N(0,1),\qquad
\varepsilon\sim N(0,0.5^2I_n).
$$

Choose a support of size $k$ uniformly at random. Assign each active coefficient independently to $+0.5$ or $-0.5$ with equal probability; set the others to zero. Generate noise independently of the design and coefficients.

The design matrix below is crossed with our grid $\theta\in\{0.4,0.5,\ldots,2.4\}$. Set $n=\lceil2\theta k\log(p-k)\rceil$; all logarithms are natural.

| Sparsity regime | Definition of $k$ | $p=128$ | $p=256$ | $p=512$ |
|---|---|---:|---:|---:|
| Linear | $\lceil0.4p\rceil$ | 52 | 103 | 205 |
| Sublinear | $\lceil0.4p/\log(0.4p)\rceil$ | 14 | 23 | 39 |
| Fractional power | $\lceil0.4p^{0.75}\rceil$ | 16 | 26 | 44 |

Run 200 replicates for each of the 189 conditions: 37,800 fits in total. Use master seed 607 with a separate random stream for each condition and replicate.

## Estimands and targets

The target is the signed support vector $\operatorname{sign}(\beta^*)$, including zeros. For each condition, estimate

$$
q=\Pr\{\operatorname{sign}(\widehat\beta)=\operatorname{sign}(\beta^*)\}.
$$

## Methods

Fit the Lasso objective

$$
\widehat\beta=\arg\min_b\left\{\frac{\|y-Xb\|_2^2}{2n}+\lambda_n\|b\|_1\right\},
\qquad
\lambda_n=\sqrt{\frac{2(0.5)^2\log(k)\log(p-k)}{n}}.
$$

Use scikit-learn's `Lasso` with `alpha=lambda_n`, `fit_intercept=False`, `tol=1e-8`, and `max_iter=10000`. Keep the generated feature scale. Treat coefficients with absolute value at most $10^{-8}$ as zero and record convergence warnings.

## Performance measures

- **Primary:** proportion of replicates with exact signed support recovery, with 95% Wilson intervals and Monte Carlo standard error $\sqrt{\widehat q(1-\widehat q)/200}$.
- **Secondary:** average numbers of false positives and false negatives, plus the proportion of fits with convergence warnings.

For Figure 1, plot fractional-power recovery probabilities against both $n$ and the realized scale $n/[2k\log(p-k)]$, reusing the same results. For Figure 2, plot recovery against this scale in three panels, one per sparsity regime, with a curve for each dimension and a reference line at 1. Summarize convergence warnings in a diagnostic plot.

## Reference

Wainwright, M. J. (2009). Sharp thresholds for high-dimensional and noisy sparsity recovery using $\ell_1$-constrained quadratic programming (Lasso). *IEEE Transactions on Information Theory*, 55(5), 2183-2202. [DOI](https://doi.org/10.1109/TIT.2009.2016018). [Author manuscript, Section VII](https://statistics.berkeley.edu/sites/default/files/tech-reports/709.pdf).
