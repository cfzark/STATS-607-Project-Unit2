# Lasso support recovery

A simulation study of exact signed support recovery using Lasso, following Figures 1 and 2 of Wainwright (2009). [ADEMP.md](ADEMP.md) describes the design; [ANALYSIS.md](ANALYSIS.md) discusses the results.

## Reproduce from a fresh clone

Install Python 3.11 with `venv` support and GNU Make. Run this command from the repository root.

```sh
make reproduce
```

The command creates or reuses `.venv`, installs the versions listed in `requirements.txt`, and uses that environment directly. It runs the full serial simulation, generates the summary and figures, then runs the tests and checks the saved trials for completeness, finite values, and convergence. The first run requires internet access to install dependencies. Allow about seven minutes for the simulation, plus setup and checks.

## Run individual stages

These targets use the Python on your PATH. To use the project environment directly, pass `PYTHON=.venv/Scripts/python.exe` on Windows or `PYTHON=.venv/bin/python` on macOS or Linux.

```sh
make test
make all       # 189 conditions, 200 replicates each
make stability-check
```

Run individual stages with `make simulate`, `make analyze`, and `make figures`. Analysis reads the saved raw results, and plotting reads the summary table. `make clean` removes the generated results.

If the dependencies are already installed, these commands work without Make.

```sh
python -m unittest discover -s tests -v
python -m src.simulation all
```

## Structure

```text
data/simulated/          Optional simulated-data cache
src/
  dgps.py               Data generation and sparsity regimes
  methods.py            Lasso fitting and penalty
  metrics.py            Recovery measures and uncertainty
  simulation.py         Simulation loop and command-line entry
  analysis.py           Summary tables
  figures.py            Figures
tests/                  Unit tests
results/
  raw/replicates.csv     Replicate-level results
  summary.csv           Results by condition
  run.json              Settings, versions, and runtime
  figures/              Two main figures and a convergence diagnostic
config.json             Simulation settings
Makefile                Run targets
requirements.txt        Python dependencies
ADEMP.md                Study design
ANALYSIS.md             Results and discussion
```

Settings are centralized in `config.json`. Each condition and replicate has a reproducible random stream based on seed 607. Raw results and the local assignment handout are ignored by Git.

## Results

The full run completed 37,800 fits in about seven minutes with no convergence warnings. Recovery increases with sample size, and rescaling brings the dimension-specific curves closer together. This reproduces the qualitative pattern; the finite-sample probabilities differ from those in the paper.

- [Sample-size rescaling](results/figures/figure1_rescaling.png)
- [Signed support recovery](results/figures/figure2_recovery.png)
- [Convergence diagnostic](results/figures/diagnostic_convergence.png)

## Reference

Wainwright, M. J. (2009). Sharp thresholds for high-dimensional and noisy sparsity recovery using l1-constrained quadratic programming (Lasso). *IEEE Transactions on Information Theory*, 55(5), 2183–2202. DOI: 10.1109/TIT.2009.2016018.
