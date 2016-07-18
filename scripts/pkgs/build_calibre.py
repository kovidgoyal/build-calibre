#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shutil
import subprocess

from .build_deps import init_env
from .constants import putenv, mkdtemp, PREFIX, CALIBRE_DIR, PYTHON, isosx, iswindows
from .utils import run, run_shell
from freeze import initialize_constants


def run_build_tests(path_to_calibre_debug, cwd_on_failure):
    p = subprocess.Popen([path_to_calibre_debug, '--test-build'])
    if p.wait() != 0:
        os.chdir(cwd_on_failure)
        run_shell()
        raise SystemExit(p.wait())


def skip_tests(*a, **kw):
    pass


def main(args):
    init_env()
    initialize_constants()
    build_dir, ext_dir = mkdtemp('build-'), mkdtemp('plugins-')
    putenv(
        CALIBRE_SETUP_EXTENSIONS_PATH=ext_dir,
        QMAKE=os.path.join(PREFIX, 'qt', 'bin', 'qmake'),
        SIP_BIN=os.path.join(PREFIX, 'bin', 'sip'),
        SW=PREFIX
    )
    os.chdir(CALIBRE_DIR)
    ld = os.path.join(PREFIX, 'qt', 'lib')
    if not iswindows:
        run('env', library_path=ld)
    cmd = [PYTHON, 'setup.py', 'build', '--build-dir=' + build_dir, '--output-dir=' + ext_dir]
    if args.only:
        cmd.append('--only=' + args.only)
    run(*cmd, library_path=ld)
    test_runner = skip_tests if args.skip_calibre_tests else run_build_tests
    if not args.only:
        if isosx:
            from freeze.osx import main as freeze
        elif iswindows:
            from freeze.windows import main as freeze
        else:
            from freeze.linux import main as freeze
        freeze(args, ext_dir, test_runner)

    # After a successful run, remove the unneeded sw directory
    shutil.rmtree(PREFIX)
