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
from pkgs.constants import SW, pkg_ext, islinux, iswindows, set_64bit
from pkgs.utils import run_shell

args = sys.argv

if hasattr(os, 'geteuid') and os.geteuid() == 0:
    import pwd
    uid, gid = pwd.getpwnam('kovid').pw_uid, pwd.getpwnam('kovid').pw_gid
    os.chown(SW, uid, gid)
    os.setgid(gid), os.setuid(uid)

if islinux:
    os.environ['HOME'] = tempfile.gettempdir()
    os.chdir(tempfile.gettempdir())

if iswindows:
    arch = args[1].decode('utf-8')
    del args[1]
    set_64bit(arch == '64')

parser = argparse.ArgumentParser(description='Build calibre dependencies')
a = parser.add_argument
a('deps', nargs='*', default=[], help='Which dependencies to build')
a('--shell', default=False, action='store_true',
  help='Start a shell in the container')
a('--clean', default=False, action='store_true',
  help='Remove previously built packages')
a('--only', default=None, help='Build only a single calibre extension')
a('--dont-strip', default=False, action='store_true', help='Dont strip the binaries when building calibre')
a('--compression-level', default='9', choices=list('123456789'), help='Level of compression for the linux calibre tarball')
a('--skip-calibre-tests', default=False, action='store_true', help='Skip the build tests when building calibre')

args = parser.parse_args(args)

if args.shell:
    from pkgs.build_deps import init_env
    dest_dir = init_env()
    try:
        raise SystemExit(run_shell())
    finally:
        shutil.rmtree(dest_dir)

if args.deps == ['calibre']:
    from pkgs.build_calibre import main
    main(args)
else:
    from pkgs.build_deps import main
    if args.clean:
        for x in os.listdir(SW):
            if x.endswith('.' + pkg_ext):
                os.remove(os.path.join(SW, x))
    main(args)
