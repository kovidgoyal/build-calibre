#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil

from .constants import build_dir
from .utils import apply_patch, simple_build, install_binaries


def main(args):
    os.chdir('source')
    # fix Malayalam encoding https://bugzilla.redhat.com/show_bug.cgi?id=654200
    apply_patch('icu.8198.revert.icu5431.patch', level=3, reverse=True)
    simple_build('--prefix=/usr --sysconfdir=/etc --mandir=/usr/share/man --sbindir=/usr/bin',
                 install_args='DESTDIR=' + build_dir())
    usr = os.path.join(build_dir(), 'usr')
    os.rename(os.path.join(usr, 'include'), os.path.join(build_dir(), 'include'))
    install_binaries(os.path.join(usr, 'lib', 'libicu*'))
    shutil.rmtree(usr)
