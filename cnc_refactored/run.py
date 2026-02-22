"""
run.py
------
One-command runner for the CNC AI trading system.
Chains install → train → signals → backtest in sequence.

Usage:
    python run.py              # full pipeline
    python run.py --skip-install
    python run.py --only train
    python run.py --only signals
    python run.py --only backtest
    python run.py --only test
"""

import argparse
import subprocess
import sys


STEPS = {
    "install":  [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
    "train":    [sys.executable, "train_model.py"],
    "signals":  [sys.executable, "main.py"],
    "backtest": [sys.executable, "backtest.py"],
    "test":     [sys.executable, "-m", "pytest", "tests/", "-v"],
}

DIVIDER = "─" * 52


def run_step(name: str, cmd: list[str]) -> bool:
    print(f"\n{DIVIDER}")
    print(f"  ▶  {name.upper()}")
    print(DIVIDER)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n✗ Step '{name}' failed (exit code {result.returncode}). Stopping.")
        return False
    print(f"\n✓ {name} complete.")
    return True


def main():
    parser = argparse.ArgumentParser(description="CNC AI System runner")
    parser.add_argument("--skip-install", action="store_true", help="Skip pip install step")
    parser.add_argument("--only", choices=STEPS.keys(), help="Run a single step only")
    args = parser.parse_args()

    if args.only:
        run_step(args.only, STEPS[args.only])
        return

    steps = list(STEPS.items())
    if args.skip_install:
        steps = [(k, v) for k, v in steps if k != "install"]

    for name, cmd in steps:
        if not run_step(name, cmd):
            sys.exit(1)

    print(f"\n{DIVIDER}")
    print("  ✓  All steps completed successfully.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
