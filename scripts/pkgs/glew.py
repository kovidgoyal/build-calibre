#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import re

from .constants import build_dir, PREFIX
from .utils import run, replace_in_file


def main(args):
    run('make GLEW_DEST={} install'.format(build_dir()))
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/glew.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/glew.pc'), re.compile(br'^libdir=.+$', re.M), b'libdir=${prefix}/lib')
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/glew.pc'), re.compile(br'^Requires:.+$', re.M), b'')
