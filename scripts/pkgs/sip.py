#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import PYTHON, MAKEOPTS, build_dir
from .utils import run


def main(args):
    b = build_dir()
    run(PYTHON, 'configure.py', '--bindir=%s/bin' % b, '--destdir=%s/lib/python2.7/site-packages' % b,
        '--sipdir=%s/share/sip' % b, '--incdir=%s/include/python2.7' % b, '--no-pyi', library_path=True)
    run('make ' + MAKEOPTS)
    run('make install')
