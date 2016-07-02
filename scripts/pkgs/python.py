#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, CFLAGS, isosx, iswindows, LIBDIR, PREFIX
from .utils import ModifiedEnv, run, simple_build, replace_in_file


def main(args):
    # Needed as the system openssl is too old, causing the _ssl module to fail
    env = {'CFLAGS': CFLAGS + ' -DHAVE_LOAD_EXTENSION', 'LD_LIBRARY_PATH': LIBDIR}
    conf = ('--prefix={} --enable-shared --with-threads --enable-ipv6 --enable-unicode={}'
            ' --with-system-expat --with-system-ffi --with-pymalloc --without-ensurepip').format(
        build_dir(), ('ucs2' if isosx or iswindows else 'ucs4'))

    with ModifiedEnv(**env):
        simple_build(conf)

    ld = build_dir() + '/lib'
    mods = '_ssl, zlib, bz2, ctypes, sqlite3'
    if not iswindows:
        mods += ', readline, _curses'
    P = os.path.join(build_dir(), 'bin', 'python')
    run(P, '-c', 'import ' + mods, library_path=ld)
    replace_in_file(P+'-config', re.compile(br'^#!.+/bin/', re.MULTILINE), '#!' + PREFIX + '/bin/')


def filter_pkg(parts):
    return 'idlelib' in parts or 'lib2to3' in parts or 'lib-tk' in parts or 'ensurepip' in parts or 'config' in parts
