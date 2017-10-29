#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import isosx
from .utils import simple_build


def main(args):
    simple_build(
        '--disable-dependency-tracking --disable-static --with-glib=no'
        ' --with-gobject=no --with-cairo=no --with-fontconfig=no --with-icu=no --with-directwrite=no' +
        ('--with-freetype=no --with-coretext=yes' if isosx else '--with-freetype=yes')
    )
