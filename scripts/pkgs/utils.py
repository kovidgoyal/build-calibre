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
import tarfile
import zipfile

from .constants import build_dir, current_source, mkdtemp, PATCHES, PYTHON, MAKEOPTS, LIBDIR, worker_env


class ModifiedEnv(object):

    def __init__(self, **kwargs):
        self.mods = kwargs

    def apply(self, mods):
        for k, val in mods.iteritems():
            if val:
                worker_env[k] = val
            else:
                worker_env.pop(k, None)

    def __enter__(self):
        self.orig = {k: worker_env.get(k) for k in self.mods}
        self.apply(self.mods)

    def __exit__(self, *args):
        self.apply(self.orig)


def run_shell():
    return subprocess.Popen(['/bin/bash']).wait()


def run(*args, **kw):
    if len(args) == 1 and isinstance(args[0], type('')):
        cmd = shlex.split(args[0])
    else:
        cmd = args
    env = os.environ.copy()
    if not kw.get('clean_env'):
        env.update(worker_env)
        if kw.get('library_path'):
            val = kw.get('library_path')
            if val is True:
                val = LIBDIR
            else:
                val = val + os.pathsep + LIBDIR
            env['LD_LIBRARY_PATH'] = val
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
        run_shell()
        raise SystemExit(1)


def extract(source):
    if source.lower().endswith('.zip'):
        with zipfile.ZipFile(source) as zf:
            zf.extractall()
    else:
        run('tar', 'xf', source)


def chdir_for_extract(name):
    tdir = mkdtemp(prefix=os.path.basename(name).split('-')[0] + '-')
    os.chdir(tdir)


def extract_source():
    source = current_source()
    chdir_for_extract(source)
    extract(source)
    x = os.listdir('.')
    if len(x) == 1:
        os.chdir(x[0])


def apply_patch(name, level=0, reverse=False):
    if not os.path.isabs(name):
        name = os.path.join(PATCHES, name)
    args = ['patch', '-p%d' % level, '-i', name]
    if reverse:
        args.insert(1, '-R')
    run(*args)


def simple_build(configure_args=(), make_args=(), install_args=(), library_path=None, override_prefix=None):
    if isinstance(configure_args, type('')):
        configure_args = shlex.split(configure_args)
    if isinstance(make_args, type('')):
        make_args = shlex.split(make_args)
    if isinstance(install_args, type('')):
        install_args = shlex.split(install_args)
    run('./configure', '--prefix=' + (override_prefix or build_dir()), *configure_args)
    run('make', *(shlex.split(MAKEOPTS) + list(make_args)))
    mi = ['make'] + list(install_args) + ['install']
    run(*mi, library_path=library_path)


def python_build(extra_args=()):
    if isinstance(extra_args, type('')):
        extra_args = shlex.split(extra_args)
    run(PYTHON, 'setup.py', 'install', '--root', build_dir(), *extra_args, library_path=True)


def replace_in_file(path, old, new):
    if isinstance(old, type('')):
        old = old.encode('utf-8')
    if isinstance(new, type('')):
        new = new.encode('utf-8')
    with open(path, 'r+b') as f:
        raw = f.read()
        if isinstance(old, bytes):
            nraw = raw.replace(old, new)
        else:
            nraw = old.sub(new, raw)
        if raw == nraw:
            raise SystemExit('Failed to patch: ' + path)
        f.seek(0), f.truncate()
        f.write(nraw)


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


def install_binaries(pattern, destdir='lib', do_symlinks=False):
    dest = os.path.join(build_dir(), destdir)
    ensure_dir(dest)
    files = glob.glob(pattern)
    files.sort(key=len, reverse=True)
    for f in files:
        dst = os.path.join(dest, os.path.basename(f))
        islink = lcopy(f, dst)
        if not islink:
            os.chmod(dst, 0o755)
    if do_symlinks:
        library_symlinks(files[0], destdir=destdir)


def install_tree(src, dest_parent='include', ignore=None):
    dest_parent = os.path.join(build_dir(), dest_parent)
    dst = os.path.join(dest_parent, os.path.basename(src))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True, ignore=ignore)
    return dst


def copy_headers(pattern, destdir='include'):
    dest = os.path.join(build_dir(), destdir)
    ensure_dir(dest)
    files = glob.glob(pattern)
    for f in files:
        dst = os.path.join(dest, os.path.basename(f))
        shutil.copy2(f, dst)


def library_symlinks(full_name, destdir='lib'):
    parts = full_name.split('.')
    idx = parts.index('so')
    basename = '.'.join(parts[:idx + 1])
    parts = parts[idx + 1:]
    for i in range(len(parts)):
        suffix = '.'.join(parts[:i])
        if suffix:
            suffix = '.' + suffix
        ln = os.path.join(build_dir(), destdir, basename + suffix)
        try:
            os.symlink(full_name, ln)
        except EnvironmentError as err:
            if err.errno != errno.EEXIST:
                raise
            os.unlink(ln)
            os.symlink(full_name, ln)


def ensure_dir(path):
    try:
        os.makedirs(path)
    except EnvironmentError as err:
        if err.errno != errno.EEXIST:
            raise


def create_package(module, src_dir, outfile):

    exclude = getattr(module, 'pkg_exclude_names', frozenset('doc man info test tests gtk-doc README'.split()))

    def filter_tar(tar_info):
        parts = tar_info.name.split('/')
        for p in parts:
            if p in exclude or p.rpartition('.')[-1] in ('pyc', 'pyo', 'la'):
                return
        if hasattr(module, 'filter_pkg') and module.filter_pkg(parts):
            return
        tar_info.uid, tar_info.gid, tar_info.mtime = 1000, 100, 0
        return tar_info

    with tarfile.open(outfile, 'w:bz2') as archive:
        for x in os.listdir(src_dir):
            path = os.path.join(src_dir, x)
            if os.path.isdir(path):
                archive.add(path, arcname=x, filter=filter_tar)


def install_package(pkg_path, dest_dir):
    with tarfile.open(pkg_path) as archive:
        archive.extractall(dest_dir)


def set_title(x):
    if sys.stdout.isatty():
        print('''\033]2;%s\007''' % x)
