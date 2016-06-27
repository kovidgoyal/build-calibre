#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil

from .constants import is64bit, CFLAGS, LDFLAGS, SW
from .utils import extract_source, run, install_binaries, install_tree


def main(args):
    extract_source()
    optflags = ['enable-ec_nistp_64_gcc_128'] if is64bit else []
    run('./config', '--prefix=/usr', '--openssldir=/etc/ssl', 'shared',
        'zlib', '-Wa,--noexecstack', CFLAGS, LDFLAGS, *optflags)
    run('make')
    run('make test', library_path=os.getcwd())
    run('make', 'INSTALL_PREFIX={}/openssl'.format(SW), 'install_sw')
    install_tree(SW + '/openssl/usr/include/openssl')
    install_binaries(SW + '/openssl/lib/lib*.so*')
    shutil.rmtree(os.path.join(SW, 'openssl'))
