#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, CFLAGS, isosx, iswindows, LIBDIR, PREFIX, islinux, PYTHON
from .utils import ModifiedEnv, run, simple_build, replace_in_file


def main(args):
    env = {'CFLAGS': CFLAGS + ' -DHAVE_LOAD_EXTENSION'}
    replace_in_file('setup.py', re.compile('def detect_tkinter.+:'), lambda m: m.group() + '\n' + ' ' * 8 + 'return 0')
    conf = (
        '--prefix={} --with-threads --enable-ipv6 --enable-unicode={}'
        ' --with-system-expat --with-pymalloc --without-ensurepip').format(
        build_dir(), ('ucs2' if isosx or iswindows else 'ucs4'))
    if islinux:
        conf += ' --with-system-ffi --enable-shared'
        # Needed as the system openssl is too old, causing the _ssl module to fail
        env['LD_LIBRARY_PATH'] = LIBDIR
    elif isosx:
        conf += ' --enable-framework={}/python --with-signal-module'.format(build_dir())
        env['MACOSX_DEPLOYMENT_TARGET'] = '10.9'  # Needed for readline detection

    with ModifiedEnv(**env):
        simple_build(conf)

    bindir = os.path.join(build_dir(), 'bin')
    P = os.path.join(bindir, 'python')
    replace_in_file(P + '-config', re.compile(br'^#!.+/bin/', re.MULTILINE), '#!' + PREFIX + '/bin/')
    if isosx:
        bindir = os.path.join(build_dir(), 'bin')
        for f in os.listdir(bindir):
            l = os.path.join(bindir, f)
            if os.path.islink(l):
                fp = os.readlink(l)
                nfp = fp.replace(build_dir(), PREFIX)
                if nfp != fp:
                    os.unlink(l)
                    os.symlink(nfp, l)


def filter_pkg(parts):
    return 'idlelib' in parts or 'lib2to3' in parts or 'lib-tk' in parts or 'ensurepip' in parts or 'config' in parts


def install_name_change_predicate(p):
    return p.endswith('/Python')


def post_install_check():
    mods = '_ssl zlib bz2 ctypes sqlite3'.split()
    if not iswindows:
        mods.extend('readline _curses'.split())
    run(PYTHON, '-c', 'import ' + ','.join(mods), library_path=True)
