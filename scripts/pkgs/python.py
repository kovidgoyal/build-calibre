#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, CFLAGS, isosx, iswindows, LIBDIR, PREFIX, islinux
from .utils import ModifiedEnv, run, simple_build, replace_in_file


def main(args):
    # Needed as the system openssl is too old, causing the _ssl module to fail
    env = {'CFLAGS': CFLAGS + ' -DHAVE_LOAD_EXTENSION'}
    replace_in_file('setup.py', re.compile('def detect_tkinter.+:'), lambda m: m.group() + '\n' + ' ' * 8 + 'return 0')
    conf = (
        '--prefix={} --with-threads --enable-ipv6 --enable-unicode={}'
        ' --with-system-expat --with-pymalloc --without-ensurepip').format(
        build_dir(), ('ucs2' if isosx or iswindows else 'ucs4'))
    if islinux:
        conf += ' --with-system-ffi --enable-shared'
        env['LD_LIBRARY_PATH'] = LIBDIR
    elif isosx:
        conf += ' --enable-framework={}/python --with-signal-module'.format(build_dir())
        # replace_in_file('setup.py', "missing.append('readline')", 'raise SystemExit("readline not found")')

    with ModifiedEnv(**env):
        simple_build(conf)

    ld = build_dir() + '/lib'
    mods = '_ssl zlib bz2 ctypes sqlite3'.split()
    if not iswindows:
        mods.extend('readline _curses'.split())
    P = os.path.join(build_dir(), 'bin', 'python')
    run(P, '-c', 'import ' + ','.join(mods), library_path=ld)
    replace_in_file(P + '-config', re.compile(br'^#!.+/bin/', re.MULTILINE), '#!' + PREFIX + '/bin/')


def filter_pkg(parts):
    return 'idlelib' in parts or 'lib2to3' in parts or 'lib-tk' in parts or 'ensurepip' in parts or 'config' in parts
