"""Independent Gaussian designs and the three sparsity regimes."""
import math

import numpy as np


def sparsity(p, regime, fraction=0.4, power=0.75):
    sizes = {
        "linear": fraction * p,
        "sublinear": fraction * p / math.log(fraction * p),
        "fractional": fraction * p**power,
    }
    k = math.ceil(sizes[regime])
    if not 1 < k < p:
        raise ValueError("The design requires 1 < k < p.")
    return k


def generate(n, p, k, rng, sigma=0.5, beta_min=0.5):
    x = rng.standard_normal((n, p))
    beta = np.zeros(p)
    support = rng.choice(p, size=k, replace=False)
    beta[support] = rng.choice([-beta_min, beta_min], size=k)
    y = x @ beta + rng.normal(0, sigma, size=n)
    return np.asfortranarray(x), y, beta
