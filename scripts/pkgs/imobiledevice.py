#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(
            openssl_CFLAGS='-I%s/include' % PREFIX,
            openssl_LIBS='-lcrypto -lssl'
    ):
        simple_build('--disable-dependency-tracking --without-cython --disable-static')
