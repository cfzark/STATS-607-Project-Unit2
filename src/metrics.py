"""Signed recovery, selection errors, and Monte Carlo uncertainty."""
from statistics import NormalDist

import numpy as np


def recovery(beta, estimate, zero_tol=1e-8):
    truth = np.sign(beta)
    fitted = np.where(np.abs(estimate) <= zero_tol, 0, np.sign(estimate))
    return {
        "success": int(np.array_equal(truth, fitted)),
        "false_positives": int(np.sum((truth == 0) & (fitted != 0))),
        "false_negatives": int(np.sum((truth != 0) & (fitted == 0))),
        "sign_errors": int(np.sum((truth != 0) & (fitted != 0) & (truth != fitted))),
    }


def binomial_summary(successes, total):
    q = successes / total
    z = NormalDist().inv_cdf(0.975)
    denominator = 1 + z**2 / total
    center = (q + z**2 / (2 * total)) / denominator
    half = z * np.sqrt(q * (1 - q) / total + z**2 / (4 * total**2)) / denominator
    return {
        "success_rate": q,
        "mcse": float(np.sqrt(q * (1 - q) / total)),
        "ci_low": max(0.0, float(center - half)),
        "ci_high": min(1.0, float(center + half)),
    }
