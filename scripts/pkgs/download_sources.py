#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os
import re
import hashlib
import json
import errno
import glob
import time
import sys
import urllib
import urlparse
import tarfile
import shutil

from .constants import SOURCES, iswindows
from .utils import tempdir, walk, run

sources_file = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'sources.json')
ext_pat = re.compile(r'\.(tar\.[a-z0-9]+)$', re.I)


def ext(fname):
    m = ext_pat.search(fname)
    if m is not None:
        return m.group(1)
    return fname.rpartition('.')[-1]


_parsed_source = None


def process_url(url, filename):
    return url.replace('{filename}', filename)


def parse_sources():
    global _parsed_source
    if _parsed_source is None:
        _parsed_source = ans = []
        for item in json.load(open(sources_file, 'rb')):
            s = item.get('windows', item.get('unix')) if iswindows else \
                item['unix']
            s['name'] = item['name']
            s['urls'] = [process_url(x, s['filename']) for x in s['urls']]
            ans.append(s)
    return _parsed_source


def verify_hash(pkg, cleanup=False):
    fname = os.path.join(SOURCES, pkg['filename'])
    alg, q = pkg['hash'].partition(':')[::2]
    q = q.strip()
    matched = False
    try:
        f = open(fname, 'rb')
    except EnvironmentError as err:
        if err.errno != errno.ENOENT:
            raise
    else:
        with f:
            if alg == 'git':
                matched = True
            else:
                h = getattr(hashlib, alg.lower())
                fhash = h(f.read()).hexdigest()
                matched = fhash == q
    if iswindows:
        def samefile(x, y):
            return os.path.normcase(os.path.abspath(x)) == os.path.normcase(os.path.abspath(y))
    else:
        samefile = os.path.samefile
    if cleanup:
        prefix = pkg['filename'].partition('-')[0]
        e = ext(pkg['filename'])
        for m in glob.glob(os.path.join(SOURCES, prefix + '-*.' + e)):
            try:
                is_samefile = samefile(fname, m)
            except EnvironmentError as err:
                if err.errno != errno.ENOENT:
                    raise
                is_samefile = False
            if not is_samefile:
                os.remove(m)
    return matched

start_time = 0


def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    if total_size == -1:
        msg = '%d MB, %d KB/s, %d seconds passed' % (
            progress_size / (1024 * 1024), speed, duration)
    else:
        percent = int(count * block_size * 100 / total_size)
        msg = "%d%%, %d MB, %d KB/s, %d seconds passed" % (
            percent, progress_size / (1024 * 1024), speed, duration)
    sys.stdout.write('\r...' + msg)
    sys.stdout.flush()


def get_pypi_url(pkg):
    parts = pkg['filename'].split('-')
    pkg_name = '-'.join(parts[:-1])
    base = 'https://pypi.python.org/simple/%s/' % pkg_name
    raw = urllib.urlopen(base).read()
    md5 = pkg['hash'].rpartition(':')[-1]
    for m in re.finditer(br'href="([^"]+%s)#md5=%s"' % (pkg['filename'], md5), raw):
        return urlparse.urljoin(base, m.group(1))


def get_git_clone(pkg, url, fname):
    with tempdir('git-') as tdir:
        run('git clone --depth=1 ' + url, cwd=tdir)
        ddir = os.listdir(tdir)[0]
        with open(os.path.join(tdir, ddir, '.git', 'HEAD'), 'rb') as f:
            ref = f.read().decode('utf-8').partition(' ')[-1].strip()
        with open(os.path.join(tdir, ddir, '.git', ref), 'rb') as f:
            h = f.read().decode('utf-8').strip()
        fhash = pkg['hash'].partition(':')[-1]
        if h != fhash:
            raise SystemExit('The hash of HEAD for %s has changed' % pkg['name'])
        fdir = os.path.join(tdir, ddir)
        for f in walk(os.path.join(fdir, '.git')):
            os.chmod(f, 0o666)  # Needed to prevent shutil.rmtree from failing
        shutil.rmtree(os.path.join(fdir, '.git'))
        with tarfile.open(fname, 'w:bz2') as tf:
            tf.add(fdir, arcname=ddir)
        shutil.rmtree(fdir)


def try_once(pkg, url):
    filename = pkg['filename']
    fname = os.path.join(SOURCES, filename)
    if url == 'pypi':
        url = get_pypi_url(pkg)
    print('Downloading', filename, 'from', url)
    if pkg['hash'].startswith('git:'):
        get_git_clone(pkg, url, fname)
    else:
        urllib.urlretrieve(url, fname, reporthook)
    if not verify_hash(pkg):
        raise SystemExit('The hash of the downloaded file: %s does not match the saved hash' % filename)


def download_pkg(pkg):
    for try_count in range(3):
        for url in pkg['urls']:
            try:
                return try_once(pkg, url)
            except Exception as err:
                import traceback
                traceback.print_exc()
                sys.stderr.flush()
                print('Download failed, with error:', type('')(err))
                sys.stdout.flush()
            finally:
                print()
    raise SystemExit(
        'Downloading of %s failed after three tries, giving up.' % pkg['name'])


def download(pkgs=None):
    sources = parse_sources()
    for pkg in sources:
        if not pkgs or pkg['name'] in pkgs:
            if not verify_hash(pkg, cleanup=True):
                download_pkg(pkg)


def filename_for_dep(dep):
    sources = parse_sources()
    for pkg in sources:
        if pkg['name'] == dep:
            return pkg['filename']
