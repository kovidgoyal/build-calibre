#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import shutil
import os

from .constants import PREFIX, PYTHON, build_dir
from .utils import python_build, run


def main(args):
    run(PYTHON, *('setup.py build_ext -I {0}/include/libxml2 -L {0}/lib'.format(PREFIX).split()), library_path=True)
    python_build()
    os.rename(os.path.join(build_dir(), 'sw/sw/lib'), os.path.join(build_dir(), 'lib'))
    shutil.rmtree(os.path.join(build_dir(), 'sw'))
