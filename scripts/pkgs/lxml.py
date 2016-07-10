#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import shutil
import os

from .constants import PREFIX, PYTHON, build_dir, isosx
from .utils import python_build, run


def main(args):
    run(PYTHON, *('setup.py build_ext -I {0}/include/libxml2 -L {0}/lib'.format(PREFIX).split()), library_path=True)
    python_build()
    ddir = 'python' if isosx else 'lib'
    os.rename(os.path.join(build_dir(), 'sw/sw/' + ddir), os.path.join(build_dir(), ddir))
    shutil.rmtree(os.path.join(build_dir(), 'sw'))
