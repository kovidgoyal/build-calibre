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
from .utils import run, run_shell, current_env
from freeze import initialize_constants, kitty_constants


def run_build_tests():
    p = subprocess.Popen([PYTHON, 'test.py'], env=current_env(library_path=True))
    if p.wait() != 0:
        run_shell()
        raise SystemExit(p.wait())


def safe_remove(x):
    if os.path.exists(x):
        if os.path.isdir(x):
            shutil.rmtree(x)
        else:
            os.unlink(x)


def build_kitty(args):
    initialize_constants()
    putenv(SW=PREFIX)
    if isosx:
        putenv(PKGCONFIG_EXE=os.path.join(PREFIX, 'bin', 'pkg-config'))
    os.chdir(KITTY_DIR)
    cmd = [PYTHON, 'setup.py']
    [safe_remove(x) for x in 'build compile_commands.json'.split()]
    if args.quick_build:
        cmd.append('build'), cmd.append('--debug')
        tdir = None
    else:
        bundle = 'macos-freeze' if isosx else 'linux-freeze'
        tdir = mkdtemp(prefix=bundle)
        cmd.append(bundle)
        if isosx:
            cmd.append('--prefix={}/{}.app'.format(tdir, kitty_constants['appname']))
        else:
            cmd.append('--prefix={}/{}'.format(tdir, kitty_constants['appname']))
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
        else:
            from freeze.linux import main as freeze
            freeze(os.path.join(tdir, kitty_constants['appname']), args)
        shutil.rmtree(tdir)

        # After a successful run, remove the unneeded sw directory
        shutil.rmtree(PREFIX)
