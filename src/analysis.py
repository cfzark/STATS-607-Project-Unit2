"""Summarize saved replicate results without rerunning simulations."""
import csv
from collections import defaultdict

import numpy as np

from .metrics import binomial_summary


def summarize(output):
    groups = defaultdict(list)
    with (output / "raw" / "replicates.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = tuple(row[field] for field in ("regime", "p", "k", "n", "theta", "theta_realized", "lambda"))
            groups[key].append(row)
    summaries = []
    for key, rows in groups.items():
        result = dict(zip(("regime", "p", "k", "n", "theta", "theta_realized", "lambda"), key))
        result["replicates"] = len(rows)
        result.update(binomial_summary(sum(int(r["success"]) for r in rows), len(rows)))
        for field in ("false_positives", "false_negatives", "sign_errors", "convergence_warning", "iterations"):
            result["mean_" + field] = float(np.mean([float(r[field]) for r in rows]))
        result["max_dual_gap"] = max(float(r["dual_gap"]) for r in rows)
        summaries.append(result)
    path = output / "summary.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    print(f"Saved {len(summaries)} conditions to {path}", flush=True)
    return summaries
