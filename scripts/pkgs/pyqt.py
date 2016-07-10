#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import PYTHON, MAKEOPTS, build_dir, PREFIX, isosx
from .utils import run


def main(args):
    b = build_dir()
    if isosx:
        b = os.path.join(b, 'python/Python.framework/Versions/2.7')
    lp = os.path.join(PREFIX, 'qt', 'lib')
    cmd = [PYTHON, 'configure.py', '--confirm-license', '--sip=%s/bin/sip' % PREFIX, '--qmake=%s/qt/bin/qmake' % PREFIX,
           '--bindir=%s/bin' % b, '--destdir=%s/lib/python2.7/site-packages' % b, '--verbose', '--sipdir=%s/share/sip/PyQt5' % b,
           '--no-stubs', '-c', '-j5', '--no-designer-plugin', '--no-qml-plugin', '--no-docstrings']
    run(*cmd, library_path=lp)
    run('make ' + MAKEOPTS, library_path=lp)
    run('make install')


def post_install_check():
    run(PYTHON, '-c', 'import sip, sipconfig; from PyQt5 import QtCore, QtGui, QtWebKit', library_path=True)
