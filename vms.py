#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import subprocess
import time
import socket
import shlex


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


def ensure_vm(name):
    if not is_vm_running(name):
        subprocess.check_call(['VBoxManage', 'startvm', name])
        time.sleep(2)
    print('Waiting for SSH server to start...')
    st = time.time()
    while not is_host_reachable(name):
        time.sleep(0.1)
    print('SSH server started in', st - time.time(), 'seconds')


def run_in_vm(name, *args, **kw):
    if len(args) == 1:
        args = shlex.split(args[0])
    p = subprocess.Popen(['ssh', name] + list(args))
    if kw.get('async'):
        return p
    if not p.wait() == 0:
        raise SystemExit(p.wait())


def shutdown_vm(name):
    if not is_vm_running(name):
        return
    isosx = name.startswith('osx-')
    cmd = 'sudo shutdown -h now' if isosx else ['shutdown.exe', '-s', '-f', '-t', '0']
    run_in_vm(name, cmd)
    while is_host_reachable(name):
        time.sleep(0.1)
    if isosx:
        # OS X VM does not shutdown cleanly
        time.sleep(5)
        subprocess.check_call(('VBoxManage controlvm %s poweroff' % name).split())
    while is_vm_running(name):
        time.sleep(0.1)
