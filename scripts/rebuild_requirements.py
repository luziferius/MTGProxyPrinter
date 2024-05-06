#!/usr/bin/env python

from pathlib import Path
from subprocess import call

repo_root = Path(__file__).parent.parent
source = repo_root / "pyproject.toml"
req = repo_root / "requirements.txt"
req_dev = repo_root / "requirements-dev.txt"
req_pack = repo_root / "requirements-package.txt"

if __name__ == "__main__":
    call(["python", "-m", "piptools", "compile", "-o", req, source])
    call(["python", "-m", "piptools", "compile", "--extra", "dev", "-o", req_dev, source])
    call(["python", "-m", "piptools", "compile", "--extra", "package", "-o", req_pack, source])
