"""Entry point for the gitobox utility.

This contains :func:`~gitobox.main.main`, which is the entry point declared to
setuptools. It is also callable directly.
"""

from __future__ import unicode_literals

import argparse
import codecs
import locale
import logging
from rpaths import Path
import sys

from gitobox import __version__ as gitobox_version
from gitobox.sync import synchronize


def setup_logging(verbosity):
    levels = [logging.CRITICAL, logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbosity, 3)]

    fmt = "%(asctime)s %(levelname)s: %(message)s"
    formatter = logging.Formatter(fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)


def main():
    """Entry point when called on the command line.
    """
    # Locale
    locale.setlocale(locale.LC_ALL, '')

    # Encoding for output streams
    if str == bytes:  # PY2
        writer = codecs.getwriter(locale.getpreferredencoding())
        o_stdout, o_stderr = sys.stdout, sys.stderr
        sys.stdout = writer(sys.stdout)
        sys.stdout.buffer = o_stdout
        sys.stderr = writer(sys.stderr)
        sys.stderr.buffer = o_stderr

    # Parses command-line

    # General options
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('--version', action='version',
                         version="gitobox version %s" % gitobox_version)
    options.add_argument('-v', '--verbose', action='count', default=1,
                         dest='verbosity',
                         help="augments verbosity level")

    parser = argparse.ArgumentParser(
        description="gitobox synchronizes a directory with a Git "
                    "repository; it is particularly useful to make a Git "
                    "branch out of changes happening in DropBox or "
                    "similar \"dump\" collaboration software",
        parents=[options])
    parser.add_argument('folder',
                        help="Folder to watch for changes")
    parser.add_argument('repository',
                        help="Git repository to synchronize")
    parser.add_argument('-b', '--branch', action='store', default='master',
                        help="Git branch to synchronize (default: master)")
    parser.add_argument('-t', '--timeout', action='store', type=int,
                        default='5',
                        help="Time to wait after last directory change before "
                        "committing (in seconds)")

    args = parser.parse_args()
    setup_logging(args.verbosity)

    synchronize(Path(args.folder), Path(args.repository), args.branch,
                args.timeout)

    sys.exit(0)


if __name__ == '__main__':
    main()
