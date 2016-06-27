#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import argparse
import importlib
from pkgs.constants import SW
from pkgs.download_sources import download

os.chown(SW, 1000, 100)
os.setegid(100), os.seteuid(1000)

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

for dep in deps:
    m = importlib.import_module('pkgs.' + dep)
    m.main(args)
