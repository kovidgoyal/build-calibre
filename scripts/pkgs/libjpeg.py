#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import isosx, PREFIX
from .utils import simple_build


def main(args):
    conf = ' --disable-dependency-tracking --enable-shared --with-jpeg8 --without-turbojpeg --disable-static'
    if isosx:
        conf += ' --host x86_64-apple-darwin NASM={}/bin/nasm'.format(PREFIX)
    simple_build(conf)
