
import argparse
import itertools
import pathlib
import typing

import subprocess


main_package = "mtg_proxy_printer"
PACKAGE_PATH = (pathlib.Path(__file__).parent.parent / main_package).resolve()
SOURCES_PATH = PACKAGE_PATH / "resources" / "resources.qrc"
TARGET_PATH = PACKAGE_PATH / "ui" / "compiled_resources.py"
T = typing.TypeVar("T")


class Namespace(typing.NamedTuple):
    command: typing.Callable[[], None]


def parse_args(args: typing.List[str] = None)-> Namespace:
    parser = argparse.ArgumentParser(
        description="Compile Qt resources into an importable module. "
                    "Compilation must be run during the packaging process"
    )
    commands = parser.add_subparsers(dest="command", help="Command to run:", required=True)
    commands.add_parser(
        "compile",
        help="Compile the resource files into an importable module"
    )
    commands.add_parser(
        "clean",
        help="Delete the compiled resources module"
    )
    parsed = parser.parse_args(args)
    parsed.command = globals()[parsed.command]
    return parsed


def split_iterable(iterable: typing.Iterable[T], chunk_size: int, /) -> typing.List[typing.Tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return list(iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ()))


def compile():
    print(f"{SOURCES_PATH=}, {TARGET_PATH=}")
    command = ("pyrcc5", "-compress", "9", str(SOURCES_PATH))  # noqa  # "pyrcc5" is a program name, not a typo
    compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
    # The resource compiler outputs > 15000 lines with extremely low line length.
    # Reduce the file size by removing a good percentage of those line breaks
    blocks = compiled.split("\\\n")
    chunks = split_iterable(blocks, 7)
    joined_chunks = ("".join(items) for items in chunks)
    compiled = "\\\n".join(joined_chunks)
    TARGET_PATH.write_text(compiled, "utf-8")


def clean():
    print(TARGET_PATH)
    TARGET_PATH.unlink(missing_ok=True)


def main():
    args = parse_args()
    args.command()


if __name__ == "__main__":
    main()
