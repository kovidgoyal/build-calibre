#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import shutil

from .constants import PREFIX, SW, build_dir, isosx, iswindows
from .utils import python_build, replace_in_file


def main(args):
    replace_in_file('setup.py', "setup_requires=['pytest-runner'],", '')
    python_build()
    ddir = 'python' if isosx else 'private' if iswindows else 'lib'
    os.rename(os.path.join(build_dir(), os.path.basename(SW), os.path.basename(PREFIX), ddir), os.path.join(build_dir(), ddir))
    shutil.rmtree(os.path.join(build_dir(), os.path.basename(SW)))
