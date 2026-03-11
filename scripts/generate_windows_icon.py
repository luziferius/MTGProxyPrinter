#!/usr/bin/env python

#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>

import argparse
from pathlib import Path

from PIL import Image


class Namespace:
    pass


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(
        description="Generates the application icon in ICO format, used on Windows."
    )
    args = parser.parse_args()
    return args


def main():
    _ = parse_args()
    root_dir = Path(__file__).parent.parent.resolve()
    src_path = root_dir / "resources" / "icons" / "MTGPP.png"
    dest_path = root_dir / "MTGPP.ico"
    with Image.open(src_path) as src:
        src.save(dest_path, "ICO")


if __name__ == "__main__":
    main()
