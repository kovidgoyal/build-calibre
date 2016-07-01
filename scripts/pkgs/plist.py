#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import CFLAGS, PREFIX
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(CFLAGS=CFLAGS + ' -I%s/include/libxml2' % PREFIX):
        simple_build('--disable-dependency-tracking --without-cython')
