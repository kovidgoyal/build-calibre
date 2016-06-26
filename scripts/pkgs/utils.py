#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import shlex
import pipes
import subprocess
import sys
import errno
import glob
import shutil
from tempfile import mkdtemp

from .constants import SOURCES, SW, SCRIPTS


class ModifiedEnv(object):

    def __init__(self, **kwargs):
        self.mods = kwargs

    def apply(self, mods):
        for k, val in mods.iteritems():
            if val:
                os.environ[k] = val
            else:
                os.environ.pop(k, None)

    def __enter__(self):
        self.orig = {k: os.environ.get(k) for k in self.mods}
        self.apply(self.mods)

    def __exit__(self, *args):
        self.apply(self.orig)


def get_source(prefix):
    for x in os.listdir(SOURCES):
        if x.lower().startswith(prefix):
            return os.path.join(SOURCES, x)


def run(*args, **kw):
    if len(args) == 1 and isinstance(args[0], type('')):
        cmd = shlex.split(args[0])
    else:
        cmd = args
    env = os.environ.copy()
    if kw.get('library_path'):
        cmd = [SCRIPTS + '/ld.sh'] + cmd
        env['LLP'] = kw['library_path']
    print(' '.join(pipes.quote(x) for x in cmd))
    try:
        p = subprocess.Popen(cmd, env=env)
    except EnvironmentError as err:
        if err.errno == errno.ENOENT:
            raise SystemExit('Could not find the program: %s' % cmd[0])
        raise
    sys.stdout.flush()
    if p.wait() != 0:
        print('The following command failed, with return code:', p.wait(),
              file=sys.stderr)
        print(' '.join(pipes.quote(x) for x in cmd))
        print('Dropping you into a shell')
        sys.stdout.flush()
        subprocess.Popen(['/bin/bash']).wait()
        raise SystemExit(1)


def extract(source):
    if source.lower().endswith('.zip'):
        run('unzip', source)
    else:
        run('tar', 'xf', source)


def extract_source(prefix):
    source = get_source(prefix)
    if not source:
        raise SystemExit('No source for %s found' % prefix)
    tdir = mkdtemp(prefix=prefix)
    os.chdir(tdir)
    extract(source)
    x = os.listdir('.')
    if len(x) == 1:
        os.chdir(x[0])


def simple_build():
    run('./configure', '--prefix=' + SW)
    run('make')
    run('make install')


def lcopy(src, dst):
    try:
        if os.path.islink(src):
            linkto = os.readlink(src)
            os.symlink(linkto, dst)
            return True
        else:
            shutil.copy(src, dst)
            return False
    except EnvironmentError as err:
        if err.errno == errno.EEXIST:
            os.unlink(dst)
            return lcopy(src, dst)


def install_binaries(pattern, dest=os.path.join(SW, 'lib')):
    files = glob.glob(pattern)
    for f in files:
        dst = os.path.join(dest, os.path.basename(f))
        islink = lcopy(f, dst)
        if not islink:
            os.chmod(dst, 0o755)


def install_tree(src, dest_parent=os.path.join(SW, 'include')):
    dst = os.path.join(dest_parent, os.path.basename(src))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)
