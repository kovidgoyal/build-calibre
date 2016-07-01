#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PREFIX, LDFLAGS, CFLAGS, LIBDIR
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(
            LIBUSB_CFLAGS="-I%s/include/libusb-1.0" % PREFIX,
            LIBUSB_LIBS='-lusb-1.0',
            CFLAGS=CFLAGS + ' -DHAVE_ICONV',
            LDFLAGS=LDFLAGS + ' -liconv',
            LD_LIBRARY_PATH=LIBDIR,
    ):
        simple_build('--disable-mtpz --disable-dependency-tracking --disable-static --with-libiconv-prefix={0} --with-udev={0}/udev'.format(PREFIX))
