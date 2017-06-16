#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .constants import is64bit, isosx, iswindows
from .utils import copy_headers, install_binaries, replace_in_file, run


def main(args):
    if iswindows:
        PL = 'x64' if is64bit else 'Win32'
        with open('dll.def', 'ab') as f:
            for symbol in (
                    'RARProcessFileW ?IsLink@@YA_NI@Z ?IsArcDir@Archive@@QEAA_NXZ'
                    ' ?GetComment@Archive@@QEAA_NPEAV?$Array@_W@@@Z ?cleandata@@YAXPEAX_K@Z').split():
                f.write(b'\r\n  ' + symbol.encode('ascii'))

        run('msbuild.exe', 'UnRARDll.vcxproj', '/t:Build', '/p:Platform=' + PL, '/p:Configuration=Release')
        install_binaries('./build/*/Release/unrar.dll', 'bin')
        install_binaries('./build/*/Release/UnRAR.lib', 'lib')
        # from .utils import run_shell
        # run_shell()
    else:
        if isosx:
            replace_in_file('makefile', 'libunrar.so', 'libunrar.dylib')
        run('make -j4 lib CXXFLAGS=-fPIC')
        install_binaries('libunrar.' + ('dylib' if isosx else 'so'), 'lib')
    copy_headers('*.hpp', destdir='include/unrar')
