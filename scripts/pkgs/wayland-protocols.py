#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
from glob import glob

from .constants import PREFIX, build_dir
from .utils import replace_in_file, simple_build


def main(args):
    simple_build()
    pcdir = os.path.join(build_dir(), 'lib/pkgconfig')
    os.makedirs(pcdir)
    for x in glob(os.path.join(build_dir(), 'share/pkgconfig/*.pc')):
        replace_in_file(x, re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
        os.rename(x, x.replace('/share/', '/lib/'))
