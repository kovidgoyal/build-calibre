#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys
import importlib
import os
import tempfile

from pkgs.constants import (
    SW, PREFIX, set_build_dir, pkg_ext, set_current_source, iswindows,
    set_tdir, mkdtemp, islinux, isosx)
from pkgs.download_sources import download, filename_for_dep
from pkgs.utils import (
    run_shell, install_package, create_package, extract_source, simple_build,
    python_build, set_title, fix_install_names, rmtree)

python_deps = 'setuptools six cssutils dateutil dnspython mechanize pygments pycrypto apsw lxml pillow netifaces psutil dbuspython macfsevents'.strip().split()

all_deps = (
    # Build tools
    'nasm cmake easylzma '
    # Python and its dependencies
    'zlib bzip2 expat sqlite libffi openssl ncurses readline python pywin32 '
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
    for x in 'libusb libmtp bzip2 iconv fontconfig'.split():
        all_deps.remove(x)
else:
    all_deps.remove('easylzma')
    all_deps.remove('pywin32')
if isosx:
    all_deps.remove('bzip2')
if not isosx:
    all_deps.remove('nasm')
    all_deps.remove('cmake')
    all_deps.remove('macfsevents')


def ensure_clear_dir(dest_dir):
    if os.path.exists(dest_dir):
        rmtree(dest_dir)
    os.makedirs(dest_dir)


def pkg_path(dep):
    return os.path.join(SW, dep + '.' + pkg_ext)


def install_pkgs(other_deps=all_deps, dest_dir=PREFIX):
    other_deps = tuple(other_deps)
    if other_deps:
        print('Installing %d previously compiled packages:' % len(other_deps), end=' ')
        sys.stdout.flush()
        for dep in other_deps:
            pkg = pkg_path(dep)
            if os.path.exists(pkg):
                print(dep, end=', ')
                sys.stdout.flush()
                install_package(pkg, dest_dir)
        print()
        sys.stdout.flush()


def build(dep, args, dest_dir):
    set_title('Building ' + dep)
    owd = os.getcwdu()
    set_current_source(filename_for_dep(dep))
    output_dir = todir = mkdtemp(prefix=dep + '-')
    set_build_dir(output_dir)
    try:
        m = importlib.import_module('pkgs.' + dep)
    except ImportError:
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), dep + '.py')):
            raise
        m = None
    tsdir = extract_source()
    try:
        if hasattr(m, 'main'):
            m.main(args)
        else:
            if dep in python_deps:
                python_build()
                output_dir = os.path.join(output_dir, os.path.basename(SW), os.path.basename(PREFIX))
            else:
                simple_build()
        if isosx:
            fix_install_names(m, output_dir)
    except Exception:
        import traceback
        traceback.print_exc()
        print('\nDropping you into a shell')
        sys.stdout.flush(), sys.stderr.flush()
        run_shell()
        raise SystemExit(1)
    create_package(m, output_dir, pkg_path(dep))
    install_package(pkg_path(dep), dest_dir)
    if hasattr(m, 'post_install_check'):
        m.post_install_check()
    os.chdir(owd)
    rmtree(todir)
    rmtree(tsdir)


def init_env(deps=all_deps):
    dest_dir = PREFIX
    ensure_clear_dir(dest_dir)
    tdir = tempfile.tempdir if iswindows else os.path.join(tempfile.gettempdir(), 't')
    ensure_clear_dir(tdir)
    set_tdir(tdir)
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
        ok = False
        try:
            build(dep, args, dest_dir)
            ok = True
        finally:
            if not ok:
                deps.insert(0, dep)
            if deps:
                print('Remaining deps:', ' '.join(deps))

    # After a successful build, remove the unneeded sw dir
    rmtree(dest_dir)
