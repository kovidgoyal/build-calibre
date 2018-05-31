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
    ft = 'no' if isosx else 'yes'
    ct = 'yes' if isosx else 'no'
    simple_build(
        '--disable-dependency-tracking --disable-static --with-glib=no --with-freetype={}'
        ' --with-gobject=no --with-cairo=no --with-fontconfig=no --with-icu=no --with-coretext={}'.format(ft, ct)
    )
    pc = os.path.join(build_dir(), 'lib/pkgconfig/harfbuzz.pc')
    replace_in_file(pc, re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
    replace_in_file(pc, re.compile(br'^exec_prefix=.+$', re.M), b'exec_prefix=${prefix}')
    replace_in_file(pc, re.compile(br'^libdir=.+$', re.M), b'libdir=${prefix}/lib')
    replace_in_file(pc, re.compile(br'^includedir=.+$', re.M), b'includedir=${prefix}/include')
