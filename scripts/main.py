#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import argparse
import shutil
import tempfile
import sys

args = sys.argv

if 'win32' in sys.platform.lower():
    arch = args[1].decode('utf-8')
    del args[1]
    os.environ['BUILD_ARCH'] = arch

from pkgs.constants import SW, pkg_ext, islinux
from pkgs.utils import run_shell


if hasattr(os, 'geteuid') and os.geteuid() == 0:
    import pwd
    uid, gid = pwd.getpwnam('kovid').pw_uid, pwd.getpwnam('kovid').pw_gid
    os.chown(SW, uid, gid)
    os.setgid(gid), os.setuid(uid)

if islinux:
    os.environ['HOME'] = tempfile.gettempdir()
    os.chdir(tempfile.gettempdir())

parser = argparse.ArgumentParser(description='Build kitty dependencies')
a = parser.add_argument
a('deps', nargs='*', default=[], help='Which dependencies to build')
a('--shell', default=False, action='store_true',
  help='Start a shell in the container')
a('--clean', default=False, action='store_true',
  help='Remove previously built packages')
a('--dont-strip', default=False, action='store_true', help='Dont strip the binaries when building kitty')
a('--compression-level', default='9', choices=list('123456789'), help='Level of compression for the linux kitty tarball')
a('--skip-kitty-tests', default=False, action='store_true', help='Skip the build tests when building kitty')
a('--sign-installers', default=False, action='store_true', help='Sign the binary installer, needs signing keys to be installed in the VMs')
a('--debug-build', default=False, action='store_true', help='Do a debug build, implies --dont-strip')
a('--quick-build', default=False, action='store_true', help='Only build kitty syncing only kitty source code and not un-installing pkgs')

args = parser.parse_args(args[1:])

if args.shell or args.deps == ['shell']:
    from pkgs.build_deps import init_env
    dest_dir = init_env()
    try:
        raise SystemExit(run_shell())
    finally:
        shutil.rmtree(dest_dir)

if args.deps == ['kitty']:
    from pkgs.build_kitty import main
    main(args)
else:
    from pkgs.build_deps import main
    if args.clean:
        for x in os.listdir(SW):
            if x.endswith('.' + pkg_ext):
                shutil.rmtree(os.path.join(SW, x))
    main(args)
