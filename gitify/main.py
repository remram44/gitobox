"""Entry point for the gitify utility.

This contains :func:`~gitify.main.main`, which is the entry point declared to
setuptools. It is also callable directly.
"""

from __future__ import unicode_literals

import argparse
import codecs
import locale
import logging
import sys

from . import __version__ as gitify_version


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
        sys.stdout = writer(sys.stdout)
        sys.stderr = writer(sys.stderr)

    # Parses command-line

    # General options
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('--version', action='version',
                         version="gitify version %s" % gitify_version)
    options.add_argument('-v', '--verbose', action='count', default=1,
                         dest='verbosity',
                         help="augments verbosity level")

    parser = argparse.ArgumentParser(
            description="gitify synchronizes a directory with a Git "
                        "repository; it is particularly useful to make a Git "
                        "branch out of changes happening in DropBox or "
                        "similar \"dump\" collaboration software",
            parents=[options])

    args = parser.parse_args()
    setup_logging(args.verbosity)

    # TODO : do stuff

    sys.exit(0)


if __name__ == '__main__':
    main()
