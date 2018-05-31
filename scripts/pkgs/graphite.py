#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

from .constants import CMAKE, PREFIX, build_dir
from .utils import ModifiedEnv, replace_in_file, run


def main(args):
    os.mkdir('build')
    os.chdir('build')
    with ModifiedEnv(
            CMAKE_INCLUDE_PATH='{}/include'.format(PREFIX),
            CMAKE_LIBRARY_PATH='{}/lib'.format(PREFIX),
    ):
            cmd = [
                CMAKE, '-G', 'Unix Makefiles', '-Wno-dev',
                '-DCMAKE_BUILD_TYPE=RELEASE',
                '-DCMAKE_INSTALL_PREFIX=' + build_dir(),
                '-Wno-dev',
                '..'
            ]
            run(*cmd)
            run('make')
            run('make install')
            replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/graphite2.pc'), re.compile(re.escape(build_dir())), PREFIX)
