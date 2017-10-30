#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

from .constants import PREFIX, build_dir, isosx
from .utils import replace_in_file, simple_build


def main(args):
    simple_build(
        '--disable-dependency-tracking --disable-static --with-glib=no'
        ' --with-gobject=no --with-cairo=no --with-fontconfig=no --with-icu=no --with-directwrite=no' +
        ('--with-freetype=no --with-coretext=yes' if isosx else '--with-freetype=yes')
    )
    pc = os.path.join(build_dir(), 'lib/pkgconfig/harfbuzz.pc')
    replace_in_file(pc, re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
    replace_in_file(pc, re.compile(br'^exec_prefix=.+$', re.M), b'exec_prefix=${prefix}')
    replace_in_file(pc, re.compile(br'^libdir=.+$', re.M), b'libdir=${prefix}/lib')
    replace_in_file(pc, re.compile(br'^includedir=.+$', re.M), b'includedir=${prefix}/include')
