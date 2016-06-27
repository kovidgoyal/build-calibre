#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import build_dir, CFLAGS, isosx, iswindows, PREFIX
from .utils import ModifiedEnv, run


def main(args):
    # Needed otherwise _ssl module fails to import because system openssl is too old
    ld_library_path = PREFIX + '/lib'
    env = {'CFLAGS': CFLAGS + ' -DHAVE_LOAD_EXTENSION'}
    conf = ('--prefix={} --enable-shared --with-threads --enable-ipv6 --enable-unicode={}'
            ' --with-system-expat --with-system-ffi --with-pymalloc --without-ensurepip').format(
        build_dir(), ('ucs2' if isosx or iswindows else 'ucs4'))

    with ModifiedEnv(**env):
        run('./configure', *conf.split(), library_path=ld_library_path)
        run('make', library_path=ld_library_path)
        run('make install', library_path=ld_library_path)

    ld = build_dir() + '/lib' + os.pathsep + ld_library_path
    mods = '_ssl, zlib, bz2, ctypes, sqlite3'
    if not iswindows:
        mods += ', readline, curses'
    run(build_dir() + '/bin/python', '-c', 'import ' + mods, library_path=ld)


def filter_pkg(parts):
    return 'idlelib' in parts or 'lib2to3' in parts or 'lib-tk' in parts or 'ensurepip' in parts or 'config' in parts
