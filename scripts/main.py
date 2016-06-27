#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import argparse
import importlib
import shutil
import tempfile
import pwd
from pkgs.constants import (
    SW, PREFIX, set_build_dir, pkg_ext, set_current_source, isosx, iswindows,
    set_tdir, mkdtemp)
from pkgs.download_sources import download, filename_for_dep
from pkgs.utils import (
    install_package, create_package, run_shell, extract_source, simple_build, python_build)

if os.geteuid() == 0:
    uid, gid = pwd.getpwnam('kovid').pw_uid, pwd.getpwnam('kovid').pw_gid
    os.chown(SW, uid, gid)
    os.setgid(gid), os.setuid(uid)
    os.putenv('HOME', tempfile.gettempdir())
    os.chdir(tempfile.gettempdir())

parser = argparse.ArgumentParser(description='Build calibre dependencies')
a = parser.add_argument
a('deps', nargs='*', default=[], help='Which dependencies to build')
a('--shell', default=False, action='store_true',
  help='Start a shell in the container')
args = parser.parse_args()

if args.shell:
    raise SystemExit(run_shell())

python_deps = [
    'setuptools', 'cssutils', 'dateutil', 'dnspython', 'mechanize', 'pygments',
    'pycrypto',
]

all_deps = [
    # Python and its dependencies
    'zlib', 'bzip2', 'expat', 'sqlite', 'libffi', 'openssl', 'ncurses', 'readline', 'python',
] + python_deps

if isosx or iswindows:
    for x in 'libffi ncurses readline'.split():
        all_deps.remove(x)
deps = args.deps or all_deps

for dep in deps:
    if dep not in all_deps:
        raise SystemExit('%s is an unknown dependency' % dep)

download(deps)

other_deps = frozenset(all_deps) - frozenset(deps)
dest_dir = PREFIX


def ensure_clear_dir(dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)
ensure_clear_dir(dest_dir)
ensure_clear_dir('t')
set_tdir(os.path.abspath('t'))


def pkg_path(dep):
    return os.path.join(SW, dep + '.' + pkg_ext)

for dep in other_deps:
    pkg = pkg_path(dep)
    if os.path.exists(pkg):
        install_package(pkg, dest_dir)


def build(dep, args):
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

for dep in deps:
    build(dep, args)
