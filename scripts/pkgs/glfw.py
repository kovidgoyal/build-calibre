#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import re
from shlex import split

from .constants import build_dir, PREFIX, CMAKE, isosx, MAKEOPTS
from .utils import run, replace_in_file


def main(args):
    os.mkdir('build'), os.chdir('build')
    cmd = [CMAKE, '-DBUILD_SHARED_LIBS=ON', '-DCMAKE_INSTALL_PREFIX=' + build_dir()]
    if isosx:
        cmd.extend('-DGLFW_USE_RETINA=ON -DGLFW_USE_MENUBAR=OFF -DGLFW_USE_CHDIR=OFF'.split())
    run(*(cmd + ['..']))
    run('make', *split(MAKEOPTS))
    run('make install')
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/glfw3.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)


def install_name_change(old_name, is_dep):
    bn = os.path.basename(old_name)
    if bn.startswith('libglfw'):
        return os.path.join(PREFIX, 'lib', bn)
    return old_name
