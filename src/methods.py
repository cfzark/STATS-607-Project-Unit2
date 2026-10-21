"""The paper's penalty and scikit-learn's coordinate descent solver."""
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import Lasso


def penalty(n, p, k, sigma):
    return float(np.sqrt(2 * sigma**2 * np.log(k) * np.log(p - k) / n))


def fit_lasso(x, y, alpha, tol=1e-8, max_iter=10000):
    model = Lasso(alpha=alpha, fit_intercept=False, tol=tol,
                  max_iter=max_iter, precompute=False, selection="cyclic")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(x, y)
    warned = any(issubclass(w.category, ConvergenceWarning) for w in caught)
    return model.coef_, {
        "convergence_warning": int(warned),
        "iterations": int(model.n_iter_),
        "dual_gap": float(model.dual_gap_),
    }
