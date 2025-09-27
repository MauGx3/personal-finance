#!/usr/bin/env python3
"""Generate per-Python constraints files for deterministic CI installs.

Usage:
  python scripts/generate_constraints.py --python /path/to/python3.10

What it does:
- Creates a temporary virtualenv using the requested python executable.
- Installs the project requirements (requirements.txt) while constrained by the global
  constraints.txt if present.
- Freezes the resulting environment to a file named `constraints-<major>.<minor>.txt`.

Notes:
- Run this from the repository root.
- You must have the requested Python interpreter installed locally.
- The script is conservative and will remove the temporary venv on completion.

This script is intended for maintainers to produce stable per-Python constraints
files that CI will consume (e.g. `constraints-3.10.txt`, `constraints-3.11.txt`).
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def run(cmd, **kwargs):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable to use (default: current Python)",
    )
    parser.add_argument("--requirements", default="requirements.txt")
    parser.add_argument("--base-constraints", default="constraints.txt")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    # determine target short name for constraints file
    try:
        out = subprocess.check_output(
            [
                args.python,
                "-c",
                "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
            ]
        )
        py_tag = out.decode().strip()
    except subprocess.CalledProcessError:
        print("Failed to query python version from", args.python)
        sys.exit(1)

    out_file = os.path.join(args.out_dir, f"constraints-{py_tag}.txt")

    tmpdir = tempfile.mkdtemp(prefix="constraints-venv-")
    venv_dir = os.path.join(tmpdir, "venv")

    try:
        print("Creating virtualenv using:", args.python)
        run([args.python, "-m", "venv", venv_dir])
        venv_py = os.path.join(venv_dir, "bin", "python")
        pip = [venv_py, "-m", "pip"]

        run(pip + ["install", "--upgrade", "pip", "setuptools", "wheel"])

        pip_install_cmd = pip + ["install"]
        if os.path.exists(args.base_constraints):
            pip_install_cmd += ["-c", args.base_constraints]

        pip_install_cmd += ["-r", args.requirements]

        print("Installing requirements into temporary venv...")
        run(pip_install_cmd)

        # freeze
        print("Generating freeze to:", out_file)
        with open(out_file, "wb") as f:
            subprocess.check_call(pip + ["freeze"], stdout=f)

        print("Wrote:", out_file)
        print("You should review / commit this file to the repository.")

    finally:
        print("Cleaning up temporary venv...", venv_dir)
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
