#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import CFLAGS, PREFIX, LIBDIR, iswindows, is64bit
from .utils import simple_build, ModifiedEnv, copy_headers, install_binaries, walk, run, replace_in_file


def main(args):
    if iswindows:
        plat = 'x64' if is64bit else 'x86'
        replace_in_file('VisualStudio/libplist/libplist/libplist.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\include\libxml2', os.path.join(PREFIX, 'include', 'libxml2'))
        replace_in_file('VisualStudio/libplist/libplist/libplist.vcxproj',
                        r'C:\cygwin64\home\kovid\sw\lib', os.path.join(PREFIX, 'lib'))
        if not is64bit:
            replace_in_file('VisualStudio/libplist/libplist/libplist.vcxproj', '$(PlatformName)\\', '')
        run('MSBuild.exe', 'VisualStudio/libplist/libplist.sln', '/t:Build', '/p:Platform=' + plat, '/p:Configuration=Release')
        copy_headers('include/plist')
        for f in walk():
            if f.endswith('.dll'):
                install_binaries(f, 'bin')
            elif f.endswith('.lib'):
                install_binaries(f, 'lib')
    else:
        with ModifiedEnv(
                CFLAGS=CFLAGS + ' -I%s/include/libxml2' % PREFIX,
                libxml2_CFLAGS=' -I%s/include/libxml2' % PREFIX,
                libxml2_LIBS='-L{} -lxml2'.format(LIBDIR)
        ):
            simple_build('--disable-dependency-tracking --without-cython')
