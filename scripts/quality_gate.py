"""
Enterprise Quality Gate
"""

import subprocess
import sys


MINIMUM_COVERAGE = 40


def main():

    command = [
        sys.executable,
        "-m",
        "pytest",
        f"--cov-fail-under={MINIMUM_COVERAGE}",
    ]

    result = subprocess.run(command)

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
