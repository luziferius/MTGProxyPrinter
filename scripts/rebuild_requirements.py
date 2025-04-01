#!/usr/bin/env python

from pathlib import Path
from subprocess import call
from concurrent.futures import ThreadPoolExecutor

repo_root = Path(__file__).parent.parent
source = repo_root / "pyproject.toml"
req = repo_root / "requirements.txt"
req_dev = repo_root / "requirements-dev.txt"
req_pack = repo_root / "requirements-package.txt"

call_params = [
    ["python", "-m", "piptools", "compile", "-o", req, source],
    ["python", "-m", "piptools", "compile", "--extra", "dev", "-o", req_dev, source],
    ["python", "-m", "piptools", "compile", "--extra", "package", "-o", req_pack, source],
]

if __name__ == "__main__":
    pool = ThreadPoolExecutor()
    for _ in pool.map(call, call_params):
        pass
    pool.shutdown()
