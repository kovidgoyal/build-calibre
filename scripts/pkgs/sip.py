#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PYTHON, MAKEOPTS, build_dir, isosx, PREFIX, iswindows
from .utils import run, replace_in_file


def main(args):
    b = build_dir()
    if isosx:
        b = os.path.join(b, 'python/Python.framework/Versions/2.7')
    elif iswindows:
        b = os.path.join(b, 'private', 'python')
    cmd = [PYTHON, 'configure.py', '--no-pyi', '--bindir=%s/bin' % build_dir()]
    cmd += ['--destdir=%s/lib/python2.7/site-packages' % b,
            '--sipdir=%s/share/sip' % b,
            '--incdir=%s/include/python2.7' % b]
    run(*cmd, library_path=True)
    if iswindows:
        run('nmake'), run('nmake install')
    else:
        run('make ' + MAKEOPTS)
        run('make install')
    q, r = build_dir(), PREFIX
    if iswindows:
        q = q.replace(os.sep, os.sep + os.sep)
        r = r.replace(os.sep, os.sep + os.sep)
    replace_in_file(os.path.join(b, 'lib/python2.7/site-packages/sipconfig.py'), q, r)
