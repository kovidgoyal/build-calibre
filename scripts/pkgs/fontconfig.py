#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(FREETYPE_CFLAGS='-I%s/include/freetype2' % PREFIX, FREETYPE_LIBS='-L%s/lib -lfreetype -lz -lbz2' % PREFIX):
        simple_build(
            '--disable-dependency-tracking --disable-static --disable-docs --with-expat=%s --with-add-fonts=/usr/share/fonts' % PREFIX, library_path=True)
