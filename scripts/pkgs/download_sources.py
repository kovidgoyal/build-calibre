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

from .constants import SOURCES, iswindows

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
            s = item.get('windows', item['unix']) if iswindows else \
                item['unix']
            s['name'] = item['name']
            s['urls'] = [process_url(x, s['filename']) for x in s['urls']]
            ans.append(s)
    return _parsed_source


def verify_hash(pkg, cleanup=False):
    fname = os.path.join(SOURCES, pkg['filename'])
    alg, q = pkg['hash'].partition(':')[::2]
    q = q.strip()
    h = getattr(hashlib, alg.lower())
    matched = False
    try:
        f = open(fname, 'rb')
    except EnvironmentError as err:
        if err.errno != errno.ENOENT:
            raise
    else:
        with f:
            fhash = h(f.read()).hexdigest()
            matched = fhash == q
    if cleanup:
        prefix = pkg['filename'].partition('-')[0]
        e = ext(pkg['filename'])
        for m in glob.glob(os.path.join(SOURCES, prefix + '-*.' + e)):
            try:
                is_samefile = os.path.samefile(fname, m)
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


def try_once(pkg, url):
    filename = pkg['filename']
    fname = os.path.join(SOURCES, filename)
    if url == 'pypi':
        url = get_pypi_url(pkg)
    print('Downloading', filename, 'from', url)
    urllib.urlretrieve(url, fname, reporthook)
    if not verify_hash(pkg):
        raise SystemExit('The hash of the downloaded file: %s does not match the saved hash' % filename)


def download_pkg(pkg):
    for try_count in range(3):
        for url in pkg['urls']:
            try:
                return try_once(pkg, url)
            except Exception as err:
                print('Download failed, with error:', type('')(err))
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
