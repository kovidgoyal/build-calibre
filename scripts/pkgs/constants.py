#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import os
import tempfile

_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
isosx = 'darwin' in _plat
islinux = not iswindows and not isosx
pkg_ext = 'pkg'
py_ver = '2.7'


def uniq(vals):
    ''' Remove all duplicates from vals, while preserving order.  '''
    vals = vals or ()
    seen = set()
    seen_add = seen.add
    return list(x for x in vals if x not in seen and not seen_add(x))


ROOT = 'C:\\' if iswindows else '/'
if isosx:
    ROOT = '/Users/shared/buildbot/'
is64bit = sys.maxsize > (1 << 32)
SW = ROOT + 'sw'
if iswindows:
    is64bit = os.environ['BUILD_ARCH'] == '64'
    SW += '64' if is64bit else '32'
SOURCES = ROOT + 'sources'
PATCHES = ROOT + 'patches'
SCRIPTS = ROOT + 'scripts'
KITTY_DIR = ROOT + 'kitty'
if iswindows:
    tempfile.tempdir = 'C:\\t\\t'
PREFIX = os.path.join(SW, 'sw')
BIN = os.path.join(PREFIX, 'bin')
PYTHON = os.path.join(PREFIX, 'private', 'python', 'python.exe') if iswindows else os.path.join(BIN, 'python3')

worker_env = {}
cygwin_paths = []

if iswindows:
    CFLAGS = CPPFLAGS = LIBDIR = LDFLAGS = ''
    from vcvars import query_vcvarsall
    env = query_vcvarsall(is64bit)
    # Remove cygwin paths from environment
    paths = [p.replace('/', os.sep) for p in env['PATH'].split(os.pathsep)]
    cygwin_paths = [p.encode('ascii') for p in paths if 'cygwin64' in p.split(os.sep)]
    paths = [p for p in paths if 'cygwin64' not in p.split(os.sep)]
    # Add the bindir to the PATH, needed for loading DLLs
    paths.insert(0, os.path.join(PREFIX, 'bin'))
    paths.insert(0, os.path.join(PREFIX, 'qt', 'bin'))
    # Needed for pywintypes27.dll which is used by the win32api module
    paths.insert(0, os.path.join(PREFIX, r'private\python\Lib\site-packages\pywin32_system32'))
    os.environ[b'PATH'] = os.pathsep.join(uniq(paths)).encode('ascii')
    for k in env:
        if k != 'PATH':
            worker_env[k] = env[k]
else:
    CFLAGS = worker_env['CFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
    CPPFLAGS = worker_env['CPPFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
    LIBDIR = os.path.join(PREFIX, 'lib')
    LDFLAGS = worker_env['LDFLAGS'] = '-L{0} -Wl,-rpath-link,{0}'.format(LIBDIR)
if isosx:
    LDFLAGS = worker_env['LDFLAGS'] = '-headerpad_max_install_names -L{}'.format(LIBDIR)
if iswindows:
    import ctypes
    from ctypes import wintypes

    class SYSTEM_INFO(ctypes.Structure):
        _fields_ = [
            ('wProcessorArchitecture', wintypes.WORD),
            ('wReserved', wintypes.WORD),
            ('dwPageSize', wintypes.DWORD),
            ('lpMinimumApplicationAddress', wintypes.LPVOID),
            ('lpMaximumApplicationAddress', wintypes.LPVOID),
            ('dwActiveProcessorMask', ctypes.c_size_t),
            ('dwNumberOfProcessors', wintypes.DWORD),
            ('dwProcessorType', wintypes.DWORD),
            ('dwAllocationGranularity', wintypes.DWORD),
            ('wProcessorLevel', wintypes.WORD),
            ('wProcessorRevision', wintypes.WORD),
        ]

    GetSystemInfo = ctypes.windll.kernel32.GetSystemInfo
    GetSystemInfo.restype = None
    GetSystemInfo.argtypes = [ctypes.POINTER(SYSTEM_INFO)]

    def cpu_count():
        sysinfo = SYSTEM_INFO()
        GetSystemInfo(sysinfo)
        num = sysinfo.dwNumberOfProcessors
        if num == 0:
            raise NotImplementedError('cannot determine number of cpus')
        return num

else:
    from multiprocessing import cpu_count

MAKEOPTS = '-j%d' % cpu_count()
PKG_CONFIG_PATH = worker_env['PKG_CONFIG_PATH'] = os.path.join(PREFIX, 'lib', 'pkgconfig')
CMAKE = os.path.join(PREFIX, 'bin', 'cmake') if isosx else 'cmake'

QT_PREFIX = os.path.join(PREFIX, 'qt')
QT_DLLS = ['Qt5' + x for x in (
    'Core', 'Gui', 'Network', 'PrintSupport', 'Positioning', 'Sensors', 'Sql',
    'Svg', 'WebKit', 'WebKitWidgets', 'Widgets', 'Multimedia', 'OpenGL',
    'MultimediaWidgets', 'Xml',  # 'XmlPatterns',
)]
QT_PLUGINS = [
    'imageformats', 'iconengines', 'mediaservice', 'platforms',
    'playlistformats', 'sqldrivers',
    # 'audio', 'printsupport', 'bearer', 'position',
]
PYQT_MODULES = ('Qt', 'QtCore', 'QtGui', 'QtNetwork',  # 'QtMultimedia', 'QtMultimediaWidgets',
                'QtPrintSupport', 'QtSensors', 'QtSvg', 'QtWebKit', 'QtWebKitWidgets', 'QtWidgets')
if islinux:
    QT_PLUGINS.append('platforminputcontexts')
    QT_DLLS += ['Qt5DBus', 'Qt5XcbQpa']
elif isosx:
    QT_DLLS += ['Qt5DBus', 'QtMacExtras']
    PYQT_MODULES += ('QtMacExtras',)
else:
    QT_DLLS += ['Qt5WinExtras']
    PYQT_MODULES += ('QtWinExtras',)

CODESIGN_KEYCHAIN = '/Users/kovid/codesign.keychain'

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
