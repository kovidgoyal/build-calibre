#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os
import re

from .constants import LIBDIR, PREFIX, build_dir
from .utils import ModifiedEnv, replace_in_file, simple_build


def main(args):
    with ModifiedEnv(LD_LIBRARY_PATH=LIBDIR):
        simple_build(
            '--disable-dependency-tracking --disable-static --enable-unicode-properties')
    for pcfile in glob.glob(os.path.join(build_dir(), 'lib/pkgconfig/*.pc')):
        replace_in_file(pcfile, re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
