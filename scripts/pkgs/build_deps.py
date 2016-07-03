#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import importlib
import shutil
import os

from pkgs.constants import (
    SW, PREFIX, set_build_dir, pkg_ext, set_current_source, iswindows,
    set_tdir, mkdtemp, islinux)
from pkgs.download_sources import download, filename_for_dep
from pkgs.utils import (
    install_package, create_package, extract_source, simple_build, python_build, set_title)

python_deps = 'setuptools six cssutils dateutil dnspython mechanize pygments pycrypto apsw lxml pillow netifaces psutil dbuspython'.strip().split()

all_deps = (
    # Python and its dependencies
    'zlib bzip2 expat sqlite libffi openssl ncurses readline python '
    # Miscellaneous dependencies
    'icu libjpeg libpng libwebp freetype fontconfig iconv libxml2 libxslt chmlib optipng mozjpeg libusb libmtp plist usbmuxd imobiledevice '
    # PDF libraries
    'poppler podofo '
    # Qt
    'libgpg-error libgcrypt glib dbus dbusglib qt sip pyqt '
).strip().split() + python_deps

if not islinux:
    for x in 'libffi ncurses readline libgpg-error libgcrypt glib dbus dbusglib dbuspython'.split():
        all_deps.remove(x)
if iswindows:
    for x in 'libusb libmtp'.split():
        all_deps.remove(x)


def ensure_clear_dir(dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)


def pkg_path(dep):
    return os.path.join(SW, dep + '.' + pkg_ext)


def install_pkgs(other_deps=all_deps, dest_dir=PREFIX):
    print('Installing previously compiled packages:', end=' ')
    sys.stdout.flush()
    for dep in other_deps:
        pkg = pkg_path(dep)
        if os.path.exists(pkg):
            print(dep, end=', ')
            sys.stdout.flush()
            install_package(pkg, dest_dir)
    print()


def build(dep, args, dest_dir):
    set_title('Building ' + dep)
    set_current_source(filename_for_dep(dep))
    output_dir = mkdtemp(prefix=dep + '-')
    set_build_dir(output_dir)
    try:
        m = importlib.import_module('pkgs.' + dep)
    except ImportError:
        m = None
    extract_source()
    if hasattr(m, 'main'):
        m.main(args)
    else:
        if dep in python_deps:
            python_build()
            # TODO: The next line will likely need to be changed on windows
            output_dir = os.path.join(output_dir, 'sw', 'sw')
        else:
            simple_build()
    create_package(m, output_dir, pkg_path(dep))
    install_package(pkg_path(dep), dest_dir)


def init_env(deps=all_deps):
    dest_dir = PREFIX
    ensure_clear_dir(dest_dir)
    ensure_clear_dir('t')
    set_tdir(os.path.abspath('t'))
    install_pkgs(deps, dest_dir)
    return dest_dir


def main(args):
    deps = args.deps or all_deps

    for dep in deps:
        if dep not in all_deps:
            raise SystemExit('%s is an unknown dependency' % dep)

    set_title('Downloading...')
    download(deps)

    other_deps = frozenset(all_deps) - frozenset(deps)
    dest_dir = init_env(other_deps)

    while deps:
        dep = deps.pop(0)
        try:
            build(dep, args, dest_dir)
        finally:
            if deps:
                print('Remaining deps:', ' '.join(deps))

    # After a successful build, remove the unneeded sw dir
    shutil.rmtree(dest_dir)
