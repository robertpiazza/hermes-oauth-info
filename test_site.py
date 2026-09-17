"""Regression check for the local OAuth-information static site."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class StaticSiteValidationTests(unittest.TestCase):
    def test_validator_accepts_the_complete_site(self) -> None:
        result = subprocess.run(
            [sys.executable, "validate.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALIDATION PASSED", result.stdout)


if __name__ == "__main__":
    unittest.main()
