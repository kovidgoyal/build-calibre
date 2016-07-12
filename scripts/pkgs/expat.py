#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import re

from .constants import iswindows
from .utils import windows_cmake_build, replace_in_file


if iswindows:
    def main(args):
        # This command causes nmake to fail and we dont want the docs anyway
        replace_in_file('CMakeLists.txt', re.compile('^add_custom_command.+ doc .+$', re.MULTILINE), '')
        windows_cmake_build(
            BUILD_tools='OFF', BUILD_examples='OFF', BUILD_tests='OFF',
            binaries='expat.dll', libraries='expat.lib', headers='../lib/expat.h ../lib/expat_external.h'
        )
