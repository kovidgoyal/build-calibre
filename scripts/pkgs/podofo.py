#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil
import glob

from .constants import PREFIX, build_dir
from .utils import run, ModifiedEnv, install_binaries


def main(args):
    # CMP0033 not supported by the version of cmake in the container
    run('sed -i /CMP0033/d CMakeLists.txt')
    # cmake cannot find libpng
    run('sed', '-i', '/FIND_PACKAGE(PNG)/cSET(PNG_INCLUDE_DIR "{}/include/libpng16")\\nSET(PNG_FOUND "1")'.format(PREFIX), 'CMakeLists.txt')
    os.mkdir('podofo-build')
    os.chdir('podofo-build')
    with ModifiedEnv(
            CMAKE_INCLUDE_PATH='{}/include'.format(PREFIX),
            CMAKE_LIBRARY_PATH='{}/lib'.format(PREFIX),
            # These are needed to avoid undefined SIZE_MAX errors on older gcc
            CXXFLAGS='-D__STDC_LIMIT_MACROS -D__STDC_CONSTANT_MACROS',
    ):
        run('cmake', '-G', 'Unix Makefiles', '-Wno-dev',
            '-DFREETYPE_INCLUDE_DIR={}/include/freetype2'.format(PREFIX),
            '-DFREETYPE_LIBRARIES=-lfreetype',
            '-DCMAKE_BUILD_TYPE=RELEASE',
            '-DPODOFO_BUILD_SHARED:BOOL=TRUE',
            '-DPODOFO_BUILD_STATIC:BOOL=FALSE',
            '-DCMAKE_INSTALL_PREFIX=' + PREFIX,
            '..')
        run('make VERBOSE=0 podofo_shared')
        install_binaries('src/libpodofo*')
        inc = os.path.join(build_dir(), 'include', 'podofo')
        os.makedirs(inc)
        shutil.copy2('podofo_config.h', inc)
        for f in glob.glob('../src/*.h'):
            shutil.copy2(f, inc)
