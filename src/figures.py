"""Recovery curves and a numerical convergence diagnostic."""
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REGIMES = ("linear", "sublinear", "fractional")
TITLES = ("Linear sparsity", "Sublinear sparsity", "Fractional-power sparsity")


def curve(ax, rows, xfield, p, color):
    rows = sorted((r for r in rows if int(r["p"]) == p), key=lambda r: float(r[xfield]))
    x, q, low, high = (np.array([float(r[f]) for r in rows]) for f in (xfield, "success_rate", "ci_low", "ci_high"))
    ax.plot(x, q, "o-", ms=3, lw=1.5, label=f"p = {p}", color=color)
    ax.fill_between(x, low, high, alpha=0.12, color=color, linewidth=0)


def plot(output):
    with (output / "summary.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    config = json.loads((output / "run.json").read_text(encoding="utf-8"))["config"]
    dimensions = sorted({int(r["p"]) for r in rows})
    repetitions = sorted({int(r["replicates"]) for r in rows})
    colors = plt.get_cmap("tab10").colors
    destination = output / "figures"
    destination.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    caption = f"Independent Gaussian design; signal magnitude = {config['beta_min']}; noise SD = {config['sigma']}; {repetitions[0]} replicates per point.\nShading: pointwise 95% Wilson intervals. Dashed line: theoretical asymptotic threshold."

    def save(fig, name):
        fig.savefig(destination / name, dpi=180, facecolor="white")
        plt.close(fig)

    def decorate(ax, scaled=True):
        ax.set_ylim(-0.03, 1.03)
        ax.set_ylabel("Exact signed recovery probability")
        ax.set_xlabel(r"Rescaled sample size $n/[2k\log(p-k)]$" if scaled else "Sample size n")
        ax.grid(alpha=0.18)
        if scaled:
            ax.axvline(1, color="0.4", ls="--", lw=1)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    fractional = [r for r in rows if r["regime"] == "fractional"]
    for ax, field in zip(axes, ("n", "theta_realized")):
        for p, color in zip(dimensions, colors):
            curve(ax, fractional, field, p, color)
        decorate(ax, scaled=field != "n")
        ax.legend(frameon=False)
    fig.suptitle("Figure 1 reproduction: sample-size rescaling (fractional-power sparsity)")
    fig.text(0.06, 0.025, caption, fontsize=8)
    fig.tight_layout(rect=(0, 0.15, 1, 0.94))
    save(fig, "figure1_rescaling.png")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True)
    for ax, regime, title in zip(axes, REGIMES, TITLES):
        for p, color in zip(dimensions, colors):
            curve(ax, [r for r in rows if r["regime"] == regime], "theta_realized", p, color)
        decorate(ax)
        ax.set_title(title)
        ax.legend(frameon=False)
    fig.suptitle("Figure 2 reproduction: Lasso signed support recovery")
    fig.text(0.05, 0.025, caption, fontsize=8)
    fig.tight_layout(rect=(0, 0.15, 1, 0.94))
    save(fig, "figure2_recovery.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    for regime, title in zip(REGIMES, TITLES):
        selected = [r for r in rows if r["regime"] == regime]
        for p in dimensions:
            group = sorted((r for r in selected if int(r["p"]) == p), key=lambda r: float(r["theta_realized"]))
            for ax, field in zip(axes, ("mean_iterations", "mean_convergence_warning")):
                ax.plot([float(r["theta_realized"]) for r in group], [float(r[field]) for r in group], "o-", ms=3, label=f"{title}, p={p}")
    for ax, title in zip(axes, ("Mean solver iterations", "Fraction with convergence warnings")):
        ax.set_title(title)
        ax.set_xlabel(r"Rescaled sample size $n/[2k\log(p-k)]$")
        ax.grid(alpha=0.18)
    axes[0].set_ylabel("Iterations")
    axes[1].set_ylabel("Warning fraction")
    axes[1].set_ylim(-0.02, 1.02)
    axes[0].legend(fontsize=7, frameon=False, ncol=2)
    fig.suptitle(f"Numerical convergence diagnostic ({repetitions[0]} replicates per point)")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "diagnostic_convergence.png")
    print(f"Saved three figures to {destination}", flush=True)
