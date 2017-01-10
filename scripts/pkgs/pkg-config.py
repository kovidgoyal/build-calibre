#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
from .constants import build_dir, PREFIX
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(LDFLAGS='-framework Foundation -framework Cocoa'):
        simple_build('--disable-debug --with-internal-glib --prefix={} --disable-host-tool --disable-dependency-tracking --with-pc-path={}'.format(
            build_dir(), os.path.join(PREFIX, 'lib', 'pkgconfig')))
