#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import shutil
import os

from .constants import PREFIX, PYTHON, build_dir, isosx, iswindows, SW
from .utils import python_build, run, replace_in_file


def main(args):
    if iswindows:
        # libxml2 does not depend on iconv in our windows build
        replace_in_file('setupinfo.py', ", 'iconv'", '')
        run(PYTHON, *('setup.py build_ext -I {0}/include;{0}/include/libxml2 -L {0}/lib'.format(PREFIX).split()))
    else:
        run(PYTHON, *('setup.py build_ext -I {0}/include/libxml2 -L {0}/lib'.format(PREFIX).split()), library_path=True)
    python_build()
    ddir = 'python' if isosx else 'private' if iswindows else 'lib'
    os.rename(os.path.join(build_dir(), os.path.basename(SW), os.path.basename(PREFIX), ddir), os.path.join(build_dir(), ddir))
    shutil.rmtree(os.path.join(build_dir(), os.path.basename(SW)))
