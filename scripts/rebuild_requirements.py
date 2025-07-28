#!/usr/bin/env python

import asyncio
import asyncio.subprocess
import itertools
from pathlib import Path

repo_root = Path(__file__).parent.parent
source = repo_root / "pyproject.toml"
req = repo_root / "requirements.txt"
req_dev = repo_root / "requirements-dev.txt"
req_pack = repo_root / "requirements-package.txt"

python_command_args = [
    ["python", "-m", "piptools", "compile", "--strip-extras", "-o", req, source],
    ["python", "-m", "piptools", "compile", "--strip-extras", "--extra", "dev", "-o", req_dev, source],
    ["python", "-m", "piptools", "compile", "--strip-extras", "--extra", "package", "-o", req_pack, source],
]
Argument = str | Path


async def run(prog: str, *args: list[Argument]):
    proc = await asyncio.create_subprocess_exec(
        prog, *args,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.wait()


async def main():
    for file in (req, req_dev, req_pack):
        file.unlink(missing_ok=True)
    tasks = itertools.starmap(run, python_command_args)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
