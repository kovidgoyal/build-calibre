#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
from future_builtins import map
import os
import re
import json
import subprocess
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from contextlib import closing


from pkgs.constants import CALIBRE_DIR, LIBDIR, worker_env, PYTHON
from pkgs.utils import walk, run

calibre_constants = {}


def read_cal_file(name):
    with open(os.path.join(CALIBRE_DIR, 'src', 'calibre', name), 'rb') as f:
        return f.read().decode('utf-8')


def initialize_constants():
    src = read_cal_file('constants.py')
    nv = re.search(r'numeric_version\s+=\s+\((\d+), (\d+), (\d+)\)', src)
    calibre_constants['version'] = '%s.%s.%s' % (nv.group(1), nv.group(2), nv.group(3))
    calibre_constants['appname'] = re.search(r'__appname__\s+=\s+(u{0,1})[\'"]([^\'"]+)[\'"]', src).group(2)
    epsrc = re.compile(r'entry_points = (\{.*?\})', re.DOTALL).search(read_cal_file('linux.py')).group(1)
    entry_points = eval(epsrc, {'__appname__': calibre_constants['appname']})

    def e2b(ep):
        return re.search(r'\s*(.*?)\s*=', ep).group(1).strip()

    def e2s(ep, base='src'):
        return (base + os.path.sep + re.search(r'.*=\s*(.*?):', ep).group(1).replace('.', '/') + '.py').strip()

    def e2m(ep):
        return re.search(r'.*=\s*(.*?)\s*:', ep).group(1).strip()

    def e2f(ep):
        return ep[ep.rindex(':') + 1:].strip()

    calibre_constants['basenames'] = basenames = {}
    calibre_constants['functions'] = functions = {}
    calibre_constants['modules'] = modules = {}
    calibre_constants['scripts'] = scripts = {}
    for x in ('console', 'gui'):
        y = x + '_scripts'
        basenames[x] = list(map(e2b, entry_points[y]))
        functions[x] = list(map(e2f, entry_points[y]))
        modules[x] = list(map(e2m, entry_points[y]))
        scripts[x] = list(map(e2s, entry_points[y]))

    src = read_cal_file('ebooks/__init__.py')
    be = re.search(r'^BOOK_EXTENSIONS\s*=\s*(\[.+?\])', src, flags=re.DOTALL | re.MULTILINE).group(1)
    calibre_constants['book_extensions'] = json.loads(be.replace("'", '"'))


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
    run(PYTHON, '-OO', '-c', 'import compileall; compileall.compile_dir("%s", force=True, quiet=True)' % basedir, library_path=True)

    for f in walk(basedir):
        ext = f.rpartition('.')[-1]
        if ext in ('py', 'pyc'):
            os.remove(f)
