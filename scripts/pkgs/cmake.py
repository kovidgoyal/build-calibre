#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(MACOSX_DEPLOYMENT_TARGET=None):
        simple_build('--no-qt-gui', configure_name='./bootstrap')


def filter_pkg(parts):
    return 'Help' in parts
