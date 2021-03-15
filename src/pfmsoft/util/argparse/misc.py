import argparse
import os
import sys
from pathlib import Path


class ArgumentParser(argparse.ArgumentParser):
    """
    Change default behavior of argparse on encounering an exception.

    # TODO needs testing

    https://stackoverflow.com/a/16942165

    :param argparse: [description]
    """

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.prog, message))


class ReadableDir(argparse.Action):
    """
    Argparse Action to ensure cmd line argument is a valid path to a directory.

    # TODO This needs some picking apart and some testing.

    https://stackoverflow.com/a/11415816

    :param argparse: [description]
    """

    def __call__(self, parser, namespace, values, option_string=None):
        dir_path: Path
        try:
            dir_path = Path(values).resolve(strict=True)
            if not dir_path.is_dir():
                parser.error("{0} is not a directory".format(dir_path))
            if os.access(dir_path, os.R_OK):
                setattr(namespace, self.dest, dir_path)
            else:
                parser.error("{0} is not a readable directory".format(dir_path))
        except FileNotFoundError:
            parser.error("{0} is not a valid path".format(values))
