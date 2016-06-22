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

from __future__ import print_function

__all__ = ['get_git_version', 'get_nicos_version']

from subprocess import Popen, PIPE
from os import path

# read config file and set environment variables
from nicos.configmod import config
from nicos.pycompat import from_utf8


def get_releasefile_path():
    # due the way we import it, the path will point to the nicos dir.
    thispath = path.normpath(path.dirname(path.dirname(__file__)))
    return path.join(thispath, 'RELEASE-VERSION')


def get_git_version(abbrev=4, cwd=None):
    try:
        p = Popen(['git', 'describe', '--abbrev=%d' % abbrev],
                  cwd=cwd or config.nicos_root, stdout=PIPE, stderr=PIPE)
        stdout, _stderr = p.communicate()
        return from_utf8(stdout.strip())
    except Exception:
        return None


def read_release_version():
    try:
        with open(get_releasefile_path(), "r") as f:
            return f.readline().strip()
    except Exception:
        return None


def write_release_version(version):
    with open(get_releasefile_path(), "w") as f:
        f.write("%s\n" % version)


def get_nicos_version(abbrev=4):
    # determine the version from git and from RELEASE-VERSION
    git_version = get_git_version(abbrev)
    release_version = read_release_version()

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
        raise ValueError('Cannot find a version number!')


if __name__ == "__main__":
    print(get_nicos_version())
