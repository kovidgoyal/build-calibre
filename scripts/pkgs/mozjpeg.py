#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import build_dir
from .utils import simple_build


def main(args):
    simple_build('--disable-dependency-tracking --disable-shared --with-jpeg8 --without-turbojpeg',
                 override_prefix=os.path.join(build_dir(), 'private', 'mozjpeg'))
