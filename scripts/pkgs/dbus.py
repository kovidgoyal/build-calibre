#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re

from .constants import build_dir, PREFIX
from .utils import simple_build, replace_in_file


def main(args):
    simple_build('--disable-dependency-tracking --disable-static '
                 ' --disable-doxygen-docs --disable-xml-docs --disable-systemd --without-systemdsystemunitdir'
                 ' --with-console-auth-dir=/run/console/ --disable-tests')
    replace_in_file(os.path.join(build_dir(), 'lib/pkgconfig/dbus-1.pc'), re.compile(br'^prefix=.+$', re.M), b'prefix=%s' % PREFIX)
