#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re
import subprocess
from multiprocessing.dummy import Pool
from contextlib import closing


from pkgs.constants import KITTY_DIR, LIBDIR, worker_env, PYTHON, cpu_count
from pkgs.utils import walk, run

kitty_constants = {}


def read_kitty_file(name):
    with open(os.path.join(KITTY_DIR, 'kitty', name), 'rb') as f:
        return f.read().decode('utf-8')


def initialize_constants():
    src = read_kitty_file('constants.py')
    nv = re.search(r'version\s+=\s+\((\d+), (\d+), (\d+)\)', src)
    kitty_constants['version'] = '%s.%s.%s' % (nv.group(1), nv.group(2), nv.group(3))
    kitty_constants['appname'] = re.search(r"^appname\s+=\s+'([^']+)'", src, flags=re.MULTILINE).group(1)


def run_worker(job, decorate=True):
    cmd, human_text = job
    human_text = human_text or b' '.join(cmd)
    env = os.environ.copy()
    env.update(worker_env)
    env['LD_LIBRARY_PATH'] = LIBDIR
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    except Exception as err:
        return False, human_text, unicode(err)
    stdout, stderr = p.communicate()
    if decorate:
        stdout = bytes(human_text) + b'\n' + (stdout or b'')
    ok = p.returncode == 0
    return ok, stdout, (stderr or b'')


def create_job(cmd, human_text=None):
    return (cmd, human_text)


def parallel_build(jobs, log=print, verbose=True):
    p = Pool(cpu_count())
    with closing(p):
        for ok, stdout, stderr in p.imap(run_worker, jobs):
            if verbose or not ok:
                log(stdout)
                if stderr:
                    log(stderr)
            if not ok:
                return False
        return True


def py_compile(basedir):
    run(PYTHON, '-OO', '-m', 'compileall', '-f', '-q', '-b', basedir, library_path=True)
    for f in walk(basedir):
        if f.endswith('.py'):
            os.remove(f)
