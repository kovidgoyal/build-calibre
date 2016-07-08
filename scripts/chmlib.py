#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import isosx
from .build import simple_build


def main(args):
    conf = '--disable-dependency-tracking'
    if isosx:
        conf += ' --disable-pread --disable-io64'
    simple_build(conf)
