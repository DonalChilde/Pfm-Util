import argparse
import os
import sys
from pathlib import Path


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.prog, message))


class ReadableDir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            dir_path = Path(values).resolve(strict=True)
        except FileNotFoundError:
            parser.error("{0} is not a valid path".format(values))

        if not dir_path.is_dir():
            parser.error("{0} is not a directory".format(dir_path))

        if os.access(dir_path, os.R_OK):
            setattr(namespace, self.dest, dir_path)
        else:
            parser.error("{0} is not a readable directory".format(dir_path))
