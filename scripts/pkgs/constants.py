#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import os
import tempfile
from multiprocessing import cpu_count

_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
isosx = 'darwin' in _plat
pkg_ext = 'tar.bz2'

SW = '/sw'
SOURCES = '/sources'
PATCHES = '/patches'
SCRIPTS = '/scripts'
is64bit = sys.maxsize > (1 << 32)
PREFIX = os.path.join(SW, 'sw')

CFLAGS = os.environ['CFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
CPPFLAGS = os.environ['CPPFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
LDFLAGS = os.environ['LDFLAGS'] = '-L' + os.path.join(PREFIX, 'lib')
os.environ['MAKEOPTS'] = '-j%d' % cpu_count()
os.environ['PKG_CONFIG_PATH'] = os.path.join(PREFIX, 'sw', 'lib', 'pkgconfig')


_build_dir = None


def build_dir():
    return _build_dir


def set_build_dir(x):
    global _build_dir
    _build_dir = x


_current_source = None


def current_source():
    return _current_source


def set_current_source(x):
    global _current_source
    _current_source = os.path.join(SOURCES, x)


_tdir = None


def set_tdir(x):
    global _tdir
    _tdir = x


def mkdtemp(prefix=''):
    return tempfile.mkdtemp(prefix=prefix, dir=_tdir)
