import csv
from pathlib import Path
import tempfile
import unittest

import numpy as np
from threadpoolctl import threadpool_limits

from src.analysis import summarize
from src.dgps import generate, sparsity
from src.methods import fit_lasso, penalty
from src.metrics import binomial_summary, recovery
from src.simulation import load_config, simulate, trial


class SimulationTests(unittest.TestCase):
    def test_design_matrix(self):
        expected = {128: (52, 14, 16), 256: (103, 23, 26), 512: (205, 39, 44)}
        for p, sizes in expected.items():
            self.assertEqual(tuple(sparsity(p, r) for r in ("linear", "sublinear", "fractional")), sizes)

    def test_dgp_properties(self):
        x, y, beta = generate(10000, 12, 3, np.random.default_rng(607))
        self.assertEqual(np.count_nonzero(beta), 3)
        np.testing.assert_array_equal(np.abs(beta[beta != 0]), 0.5)
        self.assertLess(abs(x.mean()), 0.015)
        self.assertAlmostEqual(x.var(), 1, delta=0.025)
        noise = y - x @ beta
        self.assertAlmostEqual(noise.mean(), 0, delta=0.02)
        self.assertAlmostEqual(noise.std(), 0.5, delta=0.015)

    def test_solver_matches_orthogonal_solution(self):
        x = np.sqrt(4) * np.eye(4)
        beta = np.array([0, 0.5, -0.5, 0.1])
        estimate, diagnostics = fit_lasso(x, x @ beta, alpha=0.2)
        expected = np.sign(beta) * np.maximum(np.abs(beta) - 0.2, 0)
        np.testing.assert_allclose(estimate, expected, atol=1e-12)
        self.assertEqual(diagnostics["convergence_warning"], 0)
        self.assertAlmostEqual(penalty(100, 128, 16, 0.5), np.sqrt(0.5 * np.log(16) * np.log(112) / 100))

    def test_signed_recovery_and_selection_errors(self):
        result = recovery(np.array([0, 0.5, -0.5, 0]), np.array([0.1, 0, 0.3, 1e-10]))
        self.assertEqual(result, dict(success=0, false_positives=1, false_negatives=1, sign_errors=1))
        self.assertEqual(recovery(np.array([0, 0.5]), np.array([1e-10, 0.2]))["success"], 1)

    def test_binomial_uncertainty(self):
        result = binomial_summary(100, 200)
        self.assertAlmostEqual(result["mcse"], np.sqrt(0.25 / 200))
        self.assertAlmostEqual(result["ci_low"], 0.43136086, places=7)
        self.assertAlmostEqual(result["ci_high"], 0.56863914, places=7)
        self.assertGreater(binomial_summary(0, 200)["ci_high"], 0)
        self.assertLess(binomial_summary(200, 200)["ci_low"], 1)

    def test_reproducible_across_profiles(self):
        full = load_config("config.json", "full")
        smoke = load_config("config.json", "smoke")
        with threadpool_limits(limits=1):
            first = trial(full, "fractional", 128, 1.2, 0)
            self.assertEqual(first, trial(full, "fractional", 128, 1.2, 0))
            self.assertEqual(first, trial(smoke, "fractional", 128, 1.2, 0))

    def test_raw_results_can_be_reanalyzed(self):
        config = load_config("config.json", "smoke")
        config.update(regimes=["fractional"], dimensions=[128], theta=[0.4, 2.4], replicates=3)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            simulate(config, output)
            with (output / "raw" / "replicates.csv").open(newline="") as handle:
                raw = list(csv.DictReader(handle))
            summary = summarize(output)
            self.assertEqual(len(raw), 6)
            self.assertEqual(len(summary), 2)
            for row in summary:
                successes = sum(int(r["success"]) for r in raw if r["theta"] == row["theta"])
                self.assertEqual(row["success_rate"], successes / 3)
                self.assertLessEqual(row["ci_low"], row["success_rate"] + 1e-14)
                self.assertGreaterEqual(row["ci_high"], row["success_rate"] - 1e-14)


if __name__ == "__main__":
    unittest.main()
