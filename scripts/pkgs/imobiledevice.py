#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX, LIBDIR
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(
            libplist_CFLAGS="-I{}/include".format(PREFIX),
            libplist_LIBS="-L{} -lplist".format(LIBDIR),
            libplistmm_CFLAGS="-I{}/include".format(PREFIX),
            libplistmm_LIBS="-L{} -lplist++".format(LIBDIR),
            libusbmuxd_CFLAGS="-I{}/include".format(PREFIX),
            libusbmuxd_LIBS="-L{} -lusbmuxd".format(LIBDIR),
            openssl_CFLAGS='-I%s/include' % PREFIX,
            openssl_LIBS='-lcrypto -lssl'
    ):
        simple_build('--disable-dependency-tracking --without-cython --disable-static')
