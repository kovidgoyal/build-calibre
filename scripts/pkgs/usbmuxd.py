#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PREFIX, LIBDIR, iswindows, is64bit
from .utils import simple_build, replace_in_file, ModifiedEnv, walk, run, install_binaries, copy_headers


def main(args):
    if iswindows:
        plat = 'x64' if is64bit else 'x86'
        replace_in_file('VisualStudio/libusbmuxd/libusbmuxd.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\include', os.path.join(PREFIX, 'include'))
        replace_in_file('VisualStudio/libusbmuxd/libusbmuxd.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\lib', os.path.join(PREFIX, 'lib'))
        run('MSBuild.exe', 'VisualStudio/libusbmuxd/libusbmuxd.sln', '/t:Build', '/p:Platform=' + plat, '/p:Configuration=Release')
        copy_headers('include/*.h')
        for f in walk():
            if f.endswith('.dll'):
                install_binaries(f, 'bin')
            elif f.endswith('.lib'):
                install_binaries(f, 'lib')
    else:
        # See http://www.mobileread.com/forums/showthread.php?t=255234 (prevent
        # detection of WiFi connected devices) (This patch is pre-applied in
        # the windows fork above).
        replace_in_file('src/libusbmuxd.c', 'if (di) {', 'if (di && di->product_id != 0) {')
        with ModifiedEnv(
            libplist_CFLAGS="-I{}/include".format(PREFIX),
            libplist_LIBS="-L{} -lplist".format(LIBDIR)
        ):
            simple_build('--disable-dependency-tracking')
