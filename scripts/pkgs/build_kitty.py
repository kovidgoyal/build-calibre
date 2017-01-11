#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil
import subprocess

from .build_deps import init_env
from .constants import putenv, PREFIX, KITTY_DIR, PYTHON, isosx, iswindows
from .utils import run, run_shell, ModifiedEnv, current_env
from freeze import initialize_constants


def run_build_tests():
    # OS X before 10.11 has a wcwidth() implementation that is too old
    with ModifiedEnv(ANCIENT_WCWIDTH='1'):
        p = subprocess.Popen([PYTHON, 'test.py'], env=current_env())
        if p.wait() != 0:
            run_shell()
            raise SystemExit(p.wait())


def build_kitty(args):
    initialize_constants()
    putenv(SW=PREFIX, PKGCONFIG_EXE=os.path.join(PREFIX, 'bin', 'pkg-config'))
    os.chdir(KITTY_DIR)
    cmd = [PYTHON, 'setup.py', 'build']
    if args.quick_build:
        cmd.append('--debug'), cmd.append('--incremental')
    run(*cmd)
    if not args.skip_kitty_tests:
        run_build_tests()


def main(args):
    init_env(quick_build=args.quick_build)
    build_kitty(args)
    if args.quick_build:
        subprocess.Popen([PYTHON, '.', '-c', 'from kitty.fonts.core_text import develop; develop()'], env=current_env()).wait()
    else:
        if False:
            if isosx:
                from freeze.osx import main as freeze
            elif iswindows:
                from freeze.windows import main as freeze
            else:
                from freeze.linux import main as freeze
            freeze(args)

        # After a successful run, remove the unneeded sw directory
        shutil.rmtree(PREFIX)
