# -*- coding: utf-8 -*-
# Author: Douglas Creager <dcreager@dcreager.net>
# This file is placed into the public domain.
# Updated by Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>

# Calculates the current version number.  If possible, this is the
# output of “git describe”, modified to conform to the versioning
# scheme that setuptools uses.  If “git describe” returns an error
# (most likely because we're in an unpacked copy of a release tarball,
# rather than in a git working copy), then we fall back on reading the
# contents of the RELEASE-VERSION file.

from os import path
from subprocess import PIPE, Popen

# read config file and set environment variables
from nicos import config

__all__ = ['get_git_version', 'get_nicos_version']


config.apply()


def get_releasefile_path():
    # due the way we import it, the path will point to the nicos dir.
    thispath = path.normpath(path.dirname(path.dirname(__file__)))
    return path.join(thispath, 'RELEASE-VERSION')


def translate_version(ver):
    ver = ver.lstrip('v').rsplit('-', 2)
    return '%s.post%s+%s' % tuple(ver) if len(ver) == 3 else ver[0]


def get_git_version(abbrev=4, cwd=None):
    try:
        with Popen(['git', 'describe', '--abbrev=%d' % abbrev],
                   cwd=cwd or config.nicos_root,
                   stdout=PIPE, stderr=PIPE) as p:
            stdout, stderr = p.communicate()
    except Exception as err:
        raise RuntimeError(str(err)) from None
    ver = translate_version(stdout.strip().decode('utf-8', 'ignore'))
    if ver:
        return ver
    raise RuntimeError(stderr.strip().decode('utf-8', 'ignore'))


def read_release_version():
    try:
        with open(get_releasefile_path(), 'r', encoding='utf-8') as f:
            return f.readline().strip()
    except Exception as err:
        raise RuntimeError(str(err)) from None


def write_release_version(version):
    with open(get_releasefile_path(), 'w', encoding='utf-8') as f:
        f.write("%s\n" % version)


def get_nicos_version(abbrev=4):
    # determine the version from git and from RELEASE-VERSION
    git_version = release_version = None
    git_ver_error = rel_ver_error = 'no error'
    try:
        git_version = get_git_version(abbrev)
    except RuntimeError as err:
        git_ver_error = err
    try:
        release_version = read_release_version()
    except RuntimeError as err:
        rel_ver_error = err

    # if we have a git version, it is authoritative
    if git_version:
        if git_version != release_version:
            try:
                write_release_version(git_version)
            except Exception:
                pass
        return git_version
    elif release_version:
        return release_version
    else:
        raise ValueError('Cannot find a version number.\n'
                         f'From git describe: {git_ver_error}\n'
                         f'Reading RELEASE-VERSION: {rel_ver_error}')


if __name__ == "__main__":
    print(get_nicos_version())
