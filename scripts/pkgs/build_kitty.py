#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil
import subprocess

from .build_deps import init_env
from .constants import putenv, PREFIX, KITTY_DIR, PYTHON, isosx, mkdtemp
from .utils import run, run_shell, ModifiedEnv, current_env
from freeze import initialize_constants, kitty_constants


def run_build_tests():
    # OS X has a wcwidth() implementation that is too old
    with ModifiedEnv(ANCIENT_WCWIDTH='1'):
        p = subprocess.Popen([PYTHON, 'test.py'], env=current_env())
        if p.wait() != 0:
            run_shell()
            raise SystemExit(p.wait())


def build_kitty(args):
    initialize_constants()
    putenv(SW=PREFIX)
    if isosx:
        putenv(PKGCONFIG_EXE=os.path.join(PREFIX, 'bin', 'pkg-config'))
    os.chdir(KITTY_DIR)
    cmd = [PYTHON, 'setup.py']
    if args.quick_build:
        cmd.append('build'), cmd.append('--debug'), cmd.append('--incremental')
        tdir = None
    else:
        if isosx:
            tdir = mkdtemp(prefix='osx-bundle')
            cmd.append('osx-bundle'), cmd.append('--prefix={}/{}.app'.format(tdir, kitty_constants['appname']))
        else:
            cmd.append('linux-package')
    if args.debug_build:
        if '--debug' not in cmd:
            cmd.append('--debug')
    run(*cmd, no_shell=args.quick_build, library_path=True)
    if not args.skip_kitty_tests:
        run_build_tests()
    return tdir


def main(args):
    init_env(quick_build=args.quick_build)
    tdir = build_kitty(args)
    if args.quick_build:
        subprocess.Popen([PYTHON, '.', '-c', 'from kitty.fonts.core_text import develop; develop()'], env=current_env()).wait()
    else:
        if isosx:
            from freeze.osx import main as freeze
            freeze(args, os.path.join(tdir, kitty_constants['appname'] + '.app'))
            shutil.rmtree(tdir)

        # After a successful run, remove the unneeded sw directory
        shutil.rmtree(PREFIX)
