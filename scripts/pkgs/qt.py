#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os

from .constants import CFLAGS, LDFLAGS, MAKEOPTS, build_dir
from .utils import run, apply_patch, run_shell, replace_in_file


def main(args):
    # We disable loading of bearer plugins because many distros ship with
    # broken bearer plugins that cause hangs.  At least, this was the case in
    # Qt 4.x Dont know if it is still true for Qt 5 but since we dont need
    # bearers anyway, it cant hurt.
    replace_in_file('qtbase/src/network/bearer/qnetworkconfigmanager_p.cpp', b'/bearer"', b'/bearer-disabled-by-kovid"')
    # Change pointing_hand to hand2, see
    # https://bugreports.qt.io/browse/QTBUG-41151
    replace_in_file('qtbase/src/plugins/platforms/xcb/qxcbcursor.cpp', 'pointing_hand"', 'hand2"')
    # Slim down Qt
    apply_patch('qt-slim.patch')
    # libudev is disabled because systemd based distros use libudev.so.1 while
    # non systemd based distros use libudev.so.0 (debian stable currently uses
    # libudev.so.0). And according to the incompetent udev developers, we
    # cannot use mismatching udev client and daemon versions.
    # http://www.marshut.com/yiqmk/can-apps-ship-their-own-copy-of-libudev.html
    os.mkdir('build'), os.chdir('build')
    run(('../configure -opensource -confirm-license -prefix {}/qt  -release -nomake examples -nomake tests'
         ' -no-sql-odbc -no-sql-psql -no-qml-debug -qt-xcb -no-c++11'
         ' -no-libudev -openssl -gtkstyle -icu {} {}').format(build_dir(), CFLAGS, LDFLAGS))
    # run_shell()
    run_shell
    run('make ' + MAKEOPTS, library_path=True)
    run('make install')
    with open(os.path.join(build_dir(), 'qt', 'bin', 'qt.conf'), 'wb') as f:
        f.write(b"[Paths]\nPrefix = ..\n")
