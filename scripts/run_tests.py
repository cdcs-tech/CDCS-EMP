"""
Enterprise Test Runner
"""

import subprocess
import sys


def main():
    """
    Execute the complete test suite.
    """

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
        ]
    )

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
