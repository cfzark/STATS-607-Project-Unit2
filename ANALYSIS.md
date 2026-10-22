# Analysis of Lasso support recovery

We ran 200 independent replicates for each of 189 conditions, giving 37,800 Lasso fits. The full run took about seven minutes.

## Results

Recovery increased with sample size in all three sparsity regimes. At theta = 0.4, none of the replicates recovered the signed support in any condition. At theta = 2.0, recovery rates ranged from 0.865 to 0.990. Figure 1 shows that curves for different dimensions move closer together when sample size is divided by 2k log(p-k). Figure 2 shows a broad transition from low to high recovery probability.

For p = 512 and theta = 1.0:

| Regime | Recovery probability | Mean false positives | Mean false negatives |
|---|---:|---:|---:|
| Linear | 0.395 | 0.865 | 0.000 |
| Sublinear | 0.305 | 1.295 | 0.000 |
| Fractional power | 0.340 | 1.115 | 0.000 |

At these conditions, recovery failures came from selecting extra variables. Selecting all true variables is easier than recovering the entire signed support exactly.

The simulation reproduces the paper's qualitative pattern of improved recovery with increasing sample size and alignment after rescaling. The finite-sample recovery probabilities differ from the paper's curves. With 200 replicates per condition, the largest possible Monte Carlo standard error is about 0.035. The figures include 95% Wilson intervals. Small reversals between neighboring sample sizes are consistent with Monte Carlo variation. Further experiments could examine correlated predictors and weaker signals.

## Design choices

The three sparsity regimes examine the proposed scaling under different rates of support growth. Independent Gaussian predictors and equally sized signals follow the selected experimental setting. The same penalty rule and recovery criterion apply to every condition. The sample-size grid covers both low- and high-recovery regions; dimensions up to 512 give a gradual finite-sample transition.

The independent predictors and strong, equal signals are favorable to Lasso; they do not establish performance with correlated predictors or unequal signals. I would add those settings and vary the signal-to-noise ratio to assess how sensitive the transition is to the chosen design. In practice, the results show why selecting every true predictor does not guarantee exact variable selection.

