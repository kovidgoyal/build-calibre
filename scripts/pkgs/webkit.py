#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil

from .constants import MAKEOPTS, build_dir, iswindows, PREFIX
from .utils import run, run_shell, replace_in_file


def main(args):
    # Do not build webkit2
    replace_in_file('Tools/qmake/mkspecs/features/configure.prf', 'build_webkit2 \\', '\\')

    os.mkdir('build'), os.chdir('build')
    lp = os.path.join(PREFIX, 'qt', 'lib')
    bdir = os.path.join(build_dir(), 'qt')
    qmake = os.path.join(PREFIX, 'qt', 'bin', 'qmake')
    run(qmake, 'PREFIX=' + bdir, '..', library_path=lp)
    # run_shell()
    run_shell
    if iswindows:
        run('nmake')
        run('nmake install')
    else:
        run('make ' + MAKEOPTS, library_path=lp)
        run('make INSTALL_ROOT=%s install' % bdir)
        idir = os.path.join(bdir, 'sw', 'sw', 'qt')
        for x in os.listdir(idir):
            os.rename(os.path.join(idir, x), os.path.join(bdir, x))
        shutil.rmtree(os.path.join(bdir, 'sw'))
