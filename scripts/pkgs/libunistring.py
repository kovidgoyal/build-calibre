#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from .constants import isosx
from .utils import simple_build, replace_in_file


def main(args):
    if isosx:
        replace_in_file(
            'lib/vasnprintf.c',
            '# if !(((__GLIBC__ > 2 || (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 3)) && !defined __UCLIBC__) || ((defined _WIN32 || defined __WIN32__) && ! defined __CYGWIN__))',  # noqa
            '# if 0')
    simple_build('--disable-static --disable-dependency-tracking --disable-silent-rules')
