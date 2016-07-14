#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import iswindows, PYTHON, build_dir
from .utils import run


if iswindows:
    def main(args):
        run(PYTHON, 'setup.py', 'fetch', '--all', '--missing-checksum-ok', 'build', 'install', '--root', build_dir())
