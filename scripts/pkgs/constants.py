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
islinux = not iswindows and not isosx
pkg_ext = 'tar.gz'
py_ver = '2.7'

SW = '/sw'
SOURCES = '/sources'
PATCHES = '/patches'
SCRIPTS = '/scripts'
is64bit = sys.maxsize > (1 << 32)
PREFIX = os.path.join(SW, 'sw')
BIN = os.path.join(PREFIX, 'bin')
PYTHON = os.path.join(BIN, 'python')

worker_env = {}

CFLAGS = worker_env['CFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
CPPFLAGS = worker_env['CPPFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
LIBDIR = os.path.join(PREFIX, 'lib')
LDFLAGS = worker_env['LDFLAGS'] = '-L{0} -Wl,-rpath-link,{0}'.format(LIBDIR)
if isosx:
    LDFLAGS = worker_env['LDFLAGS'] = '-headerpad_max_install_names -L{}'.format(LIBDIR)
    worker_env['MACOSX_DEPLOYMENT_TARGET'] = '10.8'
MAKEOPTS = '-j%d' % cpu_count()
PKG_CONFIG_PATH = worker_env['PKG_CONFIG_PATH'] = os.path.join(PREFIX, 'lib', 'pkgconfig')
CALIBRE_DIR = '/calibre'

QT_PREFIX = os.path.join(PREFIX, 'qt')
QT_DLLS = ['Qt5' + x for x in (
    'Core', 'Gui',  'Network', 'PrintSupport', 'Positioning', 'Sensors', 'Sql',
    'Svg', 'WebKit', 'WebKitWidgets', 'Widgets',  'Multimedia', 'OpenGL',
    'MultimediaWidgets', 'Xml',  # 'XmlPatterns',
)]
QT_PLUGINS = (
    'imageformats', 'iconengines', 'mediaservice', 'platforms',
    'playlistformats', 'sqldrivers', 'platforminputcontexts',
    # 'audio', 'printsupport', 'bearer', 'position',
)
PYQT_MODULES = ('Qt', 'QtCore', 'QtGui', 'QtNetwork',  # 'QtMultimedia', 'QtMultimediaWidgets',
                'QtPrintSupport', 'QtSensors', 'QtSvg', 'QtWebKit', 'QtWebKitWidgets', 'QtWidgets')


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


def putenv(**kw):
    for key, val in kw.iteritems():
        if not val:
            worker_env.pop(key, None)
        else:
            worker_env[key] = val


def set_64bit(val):
    global is64bit
    is64bit = val
