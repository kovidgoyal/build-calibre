#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
from future_builtins import map
import os
import re
import subprocess
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from contextlib import closing


from pkgs.constants import CALIBRE_DIR

__version__ = __appname__ = modules = functions = basenames = scripts = None


def read_cal_file(name):
    with open(os.path.join(CALIBRE_DIR, 'src', 'calibre', name), 'rb') as f:
        return f.read().decode('utf-8')


def initialize_constants():
    global __version__, __appname__, modules, functions, basenames, scripts

    src = read_cal_file('constants.py')
    nv = re.search(r'numeric_version\s+=\s+\((\d+), (\d+), (\d+)\)', src)
    __version__ = '%s.%s.%s' % (nv.group(1), nv.group(2), nv.group(3))
    __appname__ = re.search(r'__appname__\s+=\s+(u{0,1})[\'"]([^\'"]+)[\'"]',
                            src).group(2)
    epsrc = re.compile(r'entry_points = (\{.*?\})', re.DOTALL).search(read_cal_file('linux.py')).group(1)
    entry_points = eval(epsrc, {'__appname__': __appname__})

    def e2b(ep):
        return re.search(r'\s*(.*?)\s*=', ep).group(1).strip()

    def e2s(ep, base='src'):
        return (base + os.path.sep + re.search(r'.*=\s*(.*?):', ep).group(1).replace('.', '/') + '.py').strip()

    def e2m(ep):
        return re.search(r'.*=\s*(.*?)\s*:', ep).group(1).strip()

    def e2f(ep):
        return ep[ep.rindex(':') + 1:].strip()

    basenames, functions, modules, scripts = {}, {}, {}, {}
    for x in ('console', 'gui'):
        y = x + '_scripts'
        basenames[x] = list(map(e2b, entry_points[y]))
        functions[x] = list(map(e2f, entry_points[y]))
        modules[x] = list(map(e2m, entry_points[y]))
        scripts[x] = list(map(e2s, entry_points[y]))


def run_worker(job, decorate=True):
    cmd, human_text = job
    human_text = human_text or b' '.join(cmd)
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
    p = Pool(cpu_count)
    with closing(p):
        for ok, stdout, stderr in p.imap(run_worker, jobs):
            if verbose or not ok:
                log(stdout)
                if stderr:
                    log(stderr)
            if not ok:
                return False
        return True
