#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import os
from multiprocessing import cpu_count

_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
isosx = 'darwin' in _plat

SW = '/sw'
SOURCES = '/sources'
SCRIPTS = '/scripts'
is64bit = sys.maxsize > (1 << 32)

CFLAGS = os.environ['CFLAGS'] = '-I' + os.path.join(SW, 'include')
LDFLAGS = os.environ['LDFLAGS'] = '-L' + os.path.join(SW, 'lib')
os.environ['MAKEOPTS'] = '-j%d' % cpu_count()
