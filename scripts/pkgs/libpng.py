#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import glob

from .constants import PREFIX, build_dir, iswindows
from .utils import replace_in_file, simple_build, windows_cmake_build


def main(args):
    if iswindows:
        windows_cmake_build(
            PNG_SHARED='1', ZLIB_INCLUDE_DIR=os.path.join(PREFIX, 'include'), ZLIB_LIBRARY=os.path.join(PREFIX, 'lib', 'zdll.lib'),
            binaries='libpng*.dll', libraries='libpng*.lib', headers='pnglibconf.h ../png.h ../pngconf.h'
        )
    else:
        simple_build('--disable-dependency-tracking --disable-static')
        pkgconfig = os.path.join(build_dir(), 'lib', 'pkgconfig')
        for pc in glob.glob(os.path.join(pkgconfig, '*.pc')):
            replace_in_file(pc, re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
