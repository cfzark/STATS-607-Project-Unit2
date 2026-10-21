# Lasso support recovery

Reproduce the independent Gaussian simulations in Figures 1 and 2 of Wainwright (2009), examining exact signed support recovery across dimension, sparsity, and sample size. The simulation design is in [ADEMP.md](ADEMP.md).

## Setup

Use Python 3.11 or later, then run from this repository's root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
make test
make smoke       # 1,980 fits: p=128,256; 11 theta values; 3 regimes; 30 replicates
make all         # 37,800 fits: full ADEMP design, 200 replicates per condition
```

The equivalent commands without Make are:

```bash
python -m unittest discover -s tests -v
python -m src.simulation all --profile smoke
python -m src.simulation all --profile full
```

`make simulate`, `make analyze`, and `make figures` run individual stages. The latter two read saved CSV files. `make clean` removes the selected profile's generated files. Select a profile with `PROFILE=smoke` or `PROFILE=full`; for example, `make figures PROFILE=smoke`.

## Files and outputs

```text
config.json             shared settings and smoke/full profiles
data/simulated/         optional simulated-data cache
src/
  dgps.py               Gaussian data and sparsity formulas
  methods.py            penalty and Lasso fitting
  metrics.py            recovery and uncertainty measures
  simulation.py         orchestration and command-line entry point
  analysis.py           raw CSV to condition summaries
  figures.py            recovery plots and convergence diagnostic
tests/                  statistical, numerical, and reproducibility checks
results/<profile>/
  raw/replicates.csv     one row per fit, saved before summarization
  summary.csv           success rates, Wilson intervals, MCSE, selection errors
  run.json              exact settings, package versions, and measured runtime
  figures/              Figure 1, Figure 2, and convergence diagnostic
Makefile
requirements.txt
ADEMP.md
```

Each condition/replicate has its own random stream keyed by regime, dimension, theta, and replicate. Shared smoke/full conditions use identical draws. Computation uses one BLAS thread. Raw results and simulated-data caches are ignored by Git; summaries and figures can be committed. The course handout stays local.

The smoke run checks the pipeline and previews the curves; the full design supplies the final reproduction. Preliminary timing suggests 10-20 minutes for the full design on an i7-10750H; each run records its actual simulation time in `run.json`.

## Pilot results

The smoke simulation completed 1,980 fits in 9.09 seconds, with zero convergence warnings. All three sparsity regimes show increasing recovery as sample size grows. For fractional-power sparsity:

| Requested theta | p=128 | p=256 |
|---|---:|---:|
| 0.4 | 0.000 | 0.000 |
| 1.0 | 0.200 | 0.400 |
| 1.6 | 0.867 | 0.767 |
| 2.4 | 0.900 | 1.000 |

Rescaling brings the dimension-specific curves closer together. With 30 replicates per point, some neighboring estimates decrease; the Wilson intervals show the sampling uncertainty. See [Figure 1](results/smoke/figures/figure1_rescaling.png), [Figure 2](results/smoke/figures/figure2_recovery.png), and the [convergence diagnostic](results/smoke/figures/diagnostic_convergence.png). The seven tests pass, including an analytical orthogonal-design check of the Lasso solver.

## Reference

Wainwright, M. J. (2009). Sharp thresholds for high-dimensional and noisy sparsity recovery using l1-constrained quadratic programming (Lasso). *IEEE Transactions on Information Theory*, 55(5), 2183-2202. [Paper](https://doi.org/10.1109/TIT.2009.2016018).
