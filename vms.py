#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import subprocess
import time
import socket
import shlex
import tempfile
import os


def is_host_reachable(name, timeout=1):
    try:
        socket.create_connection((name, 22), timeout).close()
        return True
    except:
        return False


def is_vm_running(name):
    qname = '"%s"' % name
    try:
        lines = subprocess.check_output('VBoxManage list runningvms'.split()).decode('utf-8').splitlines()
    except Exception:
        time.sleep(1)
        lines = subprocess.check_output('VBoxManage list runningvms'.split()).decode('utf-8').splitlines()
    for line in lines:
        if line.startswith(qname):
            return True
    return False


SSH = [
    'ssh', '-o', 'User=kovid',
    '-o', 'ControlMaster=auto', '-o', 'ControlPersist=yes', '-o', 'ControlPath={}/%r@%h:%p'.format(tempfile.gettempdir())
]


def run_in_vm(name, *args, **kw):
    if len(args) == 1:
        args = shlex.split(args[0])
    p = subprocess.Popen(SSH + ['-t', name] + list(args))
    if kw.get('async'):
        return p
    if p.wait() != 0:
        raise SystemExit(p.wait())


def ensure_vm(name):
    if not is_vm_running(name):
        subprocess.Popen(['VBoxHeadless', '--startvm', name])
        time.sleep(2)
    print('Waiting for SSH server to start...')
    st = time.time()
    while not is_host_reachable(name):
        time.sleep(0.1)
    print('SSH server started in', '%.1f' % (time.time() - st), 'seconds')


def shutdown_vm(name, max_wait=15):
    start_time = time.time()
    if not is_vm_running(name):
        return
    isosx = name.startswith('osx-')
    cmd = 'sudo shutdown -h now' if isosx else ['shutdown.exe', '-s', '-f', '-t', '0']
    shp = run_in_vm(name, cmd, async=True)
    shutdown_time = time.time()

    try:
        while is_host_reachable(name) and time.time() - start_time <= max_wait:
            time.sleep(0.1)
        subprocess.Popen(SSH + ['-O', 'exit', name])
        if is_host_reachable(name):
            print('Timed out waiting for %s to shutdown cleanly, forcing shutdown' % name)
            subprocess.check_call(('VBoxManage controlvm %s poweroff' % name).split())
            return
        if isosx:
            # OS X VM hangs on shutdown, so just give it at most 5 seconds to
            # shutdown cleanly.
            max_wait = 5 + shutdown_time - start_time
        while is_vm_running(name) and time.time() - start_time <= max_wait:
            time.sleep(0.1)
        print('Timed out waiting for %s to shutdown cleanly, forcing shutdown' % name)
        subprocess.check_call(('VBoxManage controlvm %s poweroff' % name).split())
    finally:
        if shp.poll() is None:
            shp.kill()


class Rsync(object):

    excludes = frozenset({'*.pyc', '*.pyo', '*.swp', '*.swo', '*.pyj-cached', '*~', '.git'})

    def __init__(self, name):
        self.name = name

    def from_vm(self, from_, to, excludes=frozenset()):
        f = self.name + ':' + from_
        self(f, to, excludes)

    def to_vm(self, from_, to, excludes=frozenset()):
        t = self.name + ':' + to
        self(from_, t, excludes)

    def __call__(self, from_, to, excludes=frozenset()):
        ssh = ' '.join(SSH)
        if isinstance(excludes, type('')):
            excludes = excludes.split()
        excludes = frozenset(excludes) | self.excludes
        excludes = ['--exclude=' + x for x in excludes]
        cmd = ['rsync', '-a', '-e', ssh, '--delete', '--delete-excluded'] + excludes + [from_ + '/', to]
        # print(' '.join(cmd))
        p = subprocess.Popen(cmd)
        if p.wait() != 0:
            raise SystemExit(p.wait())


def to_vm(rsync, output_dir):
    print('Mirroring data to the VM...')
    calibre_dir = os.environ.get('CALIBRE_SRC_DIR', os.path.join('..', 'calibre'))
    if os.path.exists(os.path.join(calibre_dir, 'setup.py')):
        rsync.to_vm(calibre_dir, '/calibre', '/imgsrc /build /dist /manual /format_docs /icons /translations /.build-cache /tags /Changelog* *.so *.pyd')

    for x in 'scripts patches'.split():
        rsync.to_vm(x, '/' + x)

    rsync.to_vm('sources-cache', '/sources')
    rsync.to_vm('build/osx', '/sw')


def from_vm(rsync, output_dir):
    print('Mirroring data from VM...')
    rsync.from_vm('/sw', output_dir)
    rsync.from_vm('/sources', 'sources-cache')


def run_main(name, *cmd):
    run_in_vm(name, *cmd)
