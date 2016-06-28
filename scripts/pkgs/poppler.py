#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import CFLAGS, PREFIX
from .utils import run, ModifiedEnv, install_binaries


def main(args):
    with ModifiedEnv(
        CXXFLAGS=CFLAGS,
        FONTCONFIG_CFLAGS="-I{0}/include/fontconfig -I{0}/include".format(PREFIX),
        FONTCONFIG_LIBS="-L{0}/lib -lfontconfig".format(PREFIX),
        FREETYPE_CFLAGS="-I{0}/include/freetype2 -I{0}/include".format(PREFIX),
        FREETYPE_LIBS="-L{0}/lib -lfreetype -lz -lbz2".format(PREFIX),
        FREETYPE_CONFIG="{0}/bin/freetype-config".format(PREFIX),
        LIBJPEG_LIBS="-L{0}/lib -ljpeg".format(PREFIX),
        LIBPNG_LIBS="-L{0}/lib -lpng".format(PREFIX),
        LIBPNG_CFLAGS="-I{0}/include/libpng16".format(PREFIX),
        UTILS_LIBS="-lfreetype -lfontconfig -ljpeg -lpng"
    ):
        run(('./configure --prefix={} '
             '--without-x --enable-shared --disable-dependency-tracking  --disable-silent-rules '
             '--enable-zlib --enable-splash-output --disable-cairo-output --disable-poppler-glib '
             '--disable-poppler-qt4 --disable-poppler-qt5 --disable-poppler-cpp --disable-gtk-test '
             '--enable-libjpeg --enable-compile-warnings=no').format(PREFIX))
        for x in 'goo fofi splash poppler utils'.split():
            os.chdir(x)
            run('make')
            os.chdir('..')
        install_binaries('poppler/.libs/lib*.so*')
        install_binaries('utils/.libs/pdf*', 'bin')
