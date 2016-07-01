#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import LIBDIR
from .utils import simple_build, ModifiedEnv


def main(args):
    with ModifiedEnv(LD_LIBRARY_PATH=LIBDIR):
        simple_build('--disable-dependency-tracking --disable-static --disable-selinux --disable-fam --with-libiconv=gnu --with-pcre=internal')
