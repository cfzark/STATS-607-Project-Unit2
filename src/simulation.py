"""Run the reproducible simulation pipeline from the repository root."""
import argparse
import csv
import importlib.metadata
import itertools
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
from threadpoolctl import threadpool_limits

from .dgps import generate, sparsity
from .methods import fit_lasso, penalty
from .metrics import recovery

REGIME_IDS = {"linear": 0, "sublinear": 1, "fractional": 2}


def load_config(path, profile):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    selected = config.pop("profiles")[profile]
    return dict(config, **selected, profile=profile)


def trial(config, regime, p, theta, replicate):
    k = sparsity(p, regime, config["sparsity_fraction"], config["sparsity_power"])
    scale = 2 * k * math.log(p - k)
    n = math.ceil(theta * scale)
    # Keys use parameter values, so overlapping smoke/full trials are identical.
    key = (REGIME_IDS[regime], p, round(theta * 1_000_000), replicate)
    rng = np.random.default_rng(np.random.SeedSequence(config["seed"], spawn_key=key))
    x, y, beta = generate(n, p, k, rng, config["sigma"], config["beta_min"])
    alpha = penalty(n, p, k, config["sigma"])
    estimate, diagnostics = fit_lasso(x, y, alpha, config["solver_tol"], config["max_iter"])
    return dict(regime=regime, p=p, k=k, n=n, theta=theta,
                theta_realized=n / scale, replicate=replicate, **{"lambda": alpha},
                **recovery(beta, estimate, config["zero_tol"]), **diagnostics)


def simulate(config, output):
    start = time.perf_counter()
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    conditions = list(itertools.product(config["regimes"], config["dimensions"], config["theta"]))
    print(f"{len(conditions)} conditions x {config['replicates']} replicates", flush=True)
    # One BLAS thread avoids thread-launch overhead for these small matrices.
    with threadpool_limits(limits=1), (raw / "replicates.csv").open("w", newline="") as handle:
        writer = None
        for index, (regime, p, theta) in enumerate(conditions, 1):
            successes = 0
            for replicate in range(config["replicates"]):
                row = trial(config, regime, p, theta, replicate)
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=list(row))
                    writer.writeheader()
                writer.writerow(row)
                successes += row["success"]
            handle.flush()
            print(f"[{index:3d}/{len(conditions)}] {regime:10s} p={p} theta={theta:.1f}: {successes}/{config['replicates']}", flush=True)
    metadata = {
        "config": config,
        "fits": len(conditions) * config["replicates"],
        "simulation_seconds": time.perf_counter() - start,
        "python": platform.python_version(),
        "packages": {p: importlib.metadata.version(p) for p in ("numpy", "scikit-learn", "matplotlib", "threadpoolctl")},
    }
    (output / "run.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Simulation completed in {metadata['simulation_seconds']:.2f} seconds", flush=True)


def clean(output):
    # Delete only known generated files; never remove a user-selected directory.
    names = ("raw/replicates.csv", "summary.csv", "run.json", "figures/figure1_rescaling.png",
             "figures/figure2_recovery.png", "figures/diagnostic_convergence.png")
    for name in names:
        (output / name).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("all", "simulate", "analyze", "figures", "clean"))
    parser.add_argument("--profile", choices=("full", "smoke"), default="full")
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path("results") / args.profile
    if args.command == "clean":
        clean(output)
        return
    if args.command in ("all", "simulate"):
        simulate(load_config(args.config, args.profile), output)
    if args.command in ("all", "analyze"):
        from .analysis import summarize
        summarize(output)
    if args.command in ("all", "figures"):
        from .figures import plot
        plot(output)


if __name__ == "__main__":
    main()
