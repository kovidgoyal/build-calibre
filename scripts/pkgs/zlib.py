#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

from .constants import PREFIX, build_dir, iswindows
from .utils import (copy_headers, install_binaries, replace_in_file, run,
                    simple_build)

if iswindows:
    def main(args):
        run('nmake -f win32/Makefile.msc')
        run('nmake -f win32/Makefile.msc test')
        install_binaries('zlib1.dll*', 'bin')
        install_binaries('zlib.lib'), install_binaries('zdll.*')
        copy_headers('zconf.h'), copy_headers('zlib.h')
else:
    def main(args):
        simple_build()
        replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/zlib.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
