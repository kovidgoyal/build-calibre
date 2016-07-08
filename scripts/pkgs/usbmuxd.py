#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX, LIBDIR
from .utils import simple_build, replace_in_file, ModifiedEnv


def main(args):
    # See http://www.mobileread.com/forums/showthread.php?t=255234 (prevent
    # detection of WiFi connected devices)
    replace_in_file('src/libusbmuxd.c', 'if (di) {', 'if (di && di->product_id != 0) {')
    with ModifiedEnv(
        libplist_CFLAGS="-I{}/include".format(PREFIX),
        libplist_LIBS="-L{} -lplist".format(LIBDIR)
    ):
        simple_build('--disable-dependency-tracking')
