#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import argparse
import tempfile
import pwd
from pkgs.constants import SW, pkg_ext
from pkgs.utils import run_shell

if os.geteuid() == 0:
    uid, gid = pwd.getpwnam('kovid').pw_uid, pwd.getpwnam('kovid').pw_gid
    os.chown(SW, uid, gid)
    os.setgid(gid), os.setuid(uid)
    os.putenv('HOME', tempfile.gettempdir())
    os.chdir(tempfile.gettempdir())

parser = argparse.ArgumentParser(description='Build calibre dependencies')
a = parser.add_argument
a('deps', nargs='*', default=[], help='Which dependencies to build')
a('--shell', default=False, action='store_true',
  help='Start a shell in the container')
a('--clean', default=False, action='store_true',
  help='Remove previously built packages')
a('--only', default=None, help='Build only a single calibre extension')

args = parser.parse_args()

if args.shell:
    raise SystemExit(run_shell())

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
