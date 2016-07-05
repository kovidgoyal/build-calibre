#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import CFLAGS, isosx
from .utils import simple_build, ModifiedEnv


def main(args):
    cflags = CFLAGS
    if isosx:
        cflags += ' -O2 -DSQLITE_ENABLE_LOCKING_STYLE'
    with ModifiedEnv(CFLAGS=cflags):
        simple_build('--disable-dependency-tracking --disable-static')
