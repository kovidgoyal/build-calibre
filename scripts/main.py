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
from pkgs.constants import SW, set_build_dir, pkg_ext
from pkgs.download_sources import download
from pkgs.utils import install_package, create_package

os.chown(SW, 1000, 100)
os.setgid(100), os.setuid(1000)

parser = argparse.ArgumentParser(description='Build calibre dependencies')
parser.add_argument(
    'deps', nargs='*', default=[], help='Which dependencies to build'
)
args = parser.parse_args()

all_deps = [
    'zlib', 'openssl',
]
deps = args.deps or all_deps

download(deps)

other_deps = frozenset(all_deps) - frozenset(deps)
dest_dir = os.path.join(SW, 'sw')


def ensure_clear_dir(dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)
ensure_clear_dir(dest_dir)


def pkg_path(dep):
    return os.path.join(SW, dep + '.' + pkg_ext)

for dep in other_deps:
    pkg = pkg_path(dep)
    if os.path.exists(pkg):
        install_package(pkg, dest_dir)


def build(dep, args):
    output_dir = tempfile.mkdtemp(prefix=dep + '-')
    set_build_dir(output_dir)
    m = importlib.import_module('pkgs.' + dep)
    m.main(args)
    create_package(m, output_dir, pkg_path(dep))
    install_package(pkg_path(dep), dest_dir)

for dep in deps:
    build(dep, args)
