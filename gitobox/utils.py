from __future__ import unicode_literals

import random
import sys


PY3 = sys.version_info[0] == 3


if PY3:
    unicode_ = str
    izip = zip
    irange = range
    iteritems = dict.items
    itervalues = dict.values
    listvalues = lambda d: list(d.values())
else:
    unicode_ = unicode
    import itertools
    izip = itertools.izip
    irange = xrange
    iteritems = dict.iteritems
    itervalues = dict.itervalues
    listvalues = dict.values


def unique_bytestring_gen():
    """Generates unique sequences of bytes.
    """
    characters = (b"abcdefghijklmnopqrstuvwxyz"
                  b"0123456789")
    characters = [characters[i:i + 1] for i in irange(len(characters))]
    rng = random.Random()
    while True:
        letters = [rng.choice(characters) for i in irange(10)]
        yield b''.join(letters)
unique_bytestring_gen = unique_bytestring_gen()


def make_unique_bytestring():
    """Makes a unique (random) bytestring.
    """
    return next(unique_bytestring_gen)
