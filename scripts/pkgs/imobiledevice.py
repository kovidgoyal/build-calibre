#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PREFIX, LIBDIR, iswindows, is64bit
from .utils import simple_build, replace_in_file, ModifiedEnv, walk, run, install_binaries


def main(args):
    if iswindows:
        plat = 'x64' if is64bit else 'x86'
        replace_in_file('VisualStudio/libimobiledevice/libimobiledevice.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\include', os.path.join(PREFIX, 'include'))
        replace_in_file('VisualStudio/libimobiledevice/libimobiledevice.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\lib', os.path.join(PREFIX, 'lib'))
        run('MSBuild.exe', 'VisualStudio/libimobiledevice/libimobiledevice.sln', '/t:Build', '/p:Platform=' + plat, '/p:Configuration=Release')
        for f in walk():
            if f.endswith('.dll'):
                install_binaries(f, 'bin')
    else:
        with ModifiedEnv(
                libplist_CFLAGS="-I{}/include".format(PREFIX),
                libplist_LIBS="-L{} -lplist".format(LIBDIR),
                libplistmm_CFLAGS="-I{}/include".format(PREFIX),
                libplistmm_LIBS="-L{} -lplist++".format(LIBDIR),
                libusbmuxd_CFLAGS="-I{}/include".format(PREFIX),
                libusbmuxd_LIBS="-L{} -lusbmuxd".format(LIBDIR),
                openssl_CFLAGS='-I%s/include' % PREFIX,
                openssl_LIBS='-lcrypto -lssl'
        ):
            simple_build('--disable-dependency-tracking --without-cython --disable-static')
