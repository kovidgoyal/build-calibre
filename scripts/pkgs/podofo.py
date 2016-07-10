#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil
import re

from .constants import PREFIX, build_dir, islinux, isosx, CFLAGS, CMAKE, LIBDIR
from .utils import run, ModifiedEnv, install_binaries, replace_in_file, install_tree


def main(args):
    if islinux:
        # CMP0033 not supported by the version of cmake in the container
        replace_in_file('CMakeLists.txt', re.compile(br'^.+CMP0033.+$', re.MULTILINE), '')
    # cmake cannot find libpng
    replace_in_file('CMakeLists.txt', 'FIND_PACKAGE(PNG)',
                    'SET(PNG_INCLUDE_DIR "{}/include/libpng16")\nSET(PNG_FOUND "1")\nSET(PNG_LIBRARIES "-lpng16")'.format(PREFIX))
    os.mkdir('podofo-build')
    os.chdir('podofo-build')
    with ModifiedEnv(
            CMAKE_INCLUDE_PATH='{}/include'.format(PREFIX),
            CMAKE_LIBRARY_PATH='{}/lib'.format(PREFIX),
            # These are needed to avoid undefined SIZE_MAX errors on older gcc
            # (SIZE_MAX goes away in podofo 0.9.5)
            CXXFLAGS='-D__STDC_LIMIT_MACROS -D__STDC_CONSTANT_MACROS',
    ):
        cmd = [
            CMAKE, '-G', 'Unix Makefiles', '-Wno-dev',
            '-DFREETYPE_INCLUDE_DIR={}/include/freetype2'.format(PREFIX),
            '-DFREETYPE_LIBRARIES=-lfreetype',
            '-DCMAKE_BUILD_TYPE=RELEASE',
            '-DPODOFO_BUILD_SHARED:BOOL=TRUE',
            '-DPODOFO_BUILD_STATIC:BOOL=FALSE',
            '-DCMAKE_INSTALL_PREFIX=' + PREFIX,
            '..'
        ]
        if isosx:
            # We set c++98 and libstdc++ as PoDoFo does not use C++11 and without that it
            # will be compiled with C++11 and linked against libc++, which means the PoDoFo
            # calibre extension would also have to be compiled and liked that way.
            cmd.insert(-2, '-DCMAKE_CXX_FLAGS=' + CFLAGS + ' -std=c++98 -stdlib=libstdc++')
        run(*cmd)
        run('make VERBOSE=0 podofo_shared')
        install_binaries('src/libpodofo*')
        inc = os.path.join(build_dir(), 'include', 'podofo')
        os.rename(install_tree('../src', ignore=lambda d, children: [x for x in children if not x.endswith('.h') and '.' in x]), inc)
        shutil.copy2('podofo_config.h', inc)
        ldir = os.path.join(build_dir(), 'lib')
        libs = {os.path.realpath(os.path.join(ldir, x)) for x in os.listdir(ldir)}
        if islinux:
            # libpodofo.so has RPATH set which is just wrong. Remove it.
            run('chrpath', '--delete', *list(libs))

pkg_exclude_names = frozenset()


def install_name_change(old_name, is_dep):
    # since we build podofo in-place the normal install name change logic does
    # not work
    return os.path.join(LIBDIR, os.path.basename(old_name))
