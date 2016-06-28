#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX
from .utils import simple_build


def main(args):
    simple_build(
        '--disable-dependency-tracking --disable-static --enable-shared --without-python --without-debug --with-libxml-prefix={0}'
        ' --with-libxml-include-prefix={0}/include/libxml2'.format(PREFIX))
