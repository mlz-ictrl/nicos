#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
"""
Utility routines for nicos file finding


This modules contains helper functions to find e.g. setupfiles etc.
"""

import os
import re
from configparser import ConfigParser
from os import path

SETUPNAME_RE = re.compile(r'[-\w]+$')


def iterSetups(paths):
    """Iterate over full file names of all setups within the given paths."""
    for rootpath in paths:
        for root, _, files in os.walk(rootpath, topdown=False):
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                filepath = path.join(root, filename)
                setupname = path.splitext(path.basename(filepath))[0]
                if SETUPNAME_RE.match(setupname):
                    yield (setupname, filepath)


def findSetup(paths, setupname):
    """Return, if found, the full filename for a given setup name."""
    for (fpsetupname, filepath) in iterSetups(paths):
        if fpsetupname == setupname:
            return filepath


def findNicosFacilityDirs(where):
    for facility in sorted(os.listdir(where)):
        full = path.join(where, facility)
        if facility.startswith('nicos_') and path.isdir(full):
            yield facility, full


def findNicosInstrumentSubDirs(parent, facility=''):
    for instr in sorted(os.listdir(parent)):
        fullinstr = path.join(parent, instr)
        if path.isfile(path.join(fullinstr, 'nicos.conf')):
            yield instr, facility, fullinstr


def findAllNicosInstrumentDirs(root):
    for facility, full in findNicosFacilityDirs(root):
        yield from findNicosInstrumentSubDirs(full, facility)


def findInstrGuiConfigs(where):
    for guiconf in sorted(os.listdir(where)):
        if 'guiconf' in guiconf and guiconf.endswith('.py'):
            yield guiconf, path.join(where, guiconf)


def findSetupRoots(filename):
    """Find nicos.conf and resolve setup root directories."""
    dirname = path.dirname(filename)
    while not path.isfile(path.join(dirname, 'nicos.conf')):
        new_dirname = path.dirname(dirname)
        if new_dirname == dirname:
            # we arrived at the root directory (/ or X:\) without finding
            # nicos.conf, let's just search in the setup's directory
            return (path.dirname(filename),)
        dirname = new_dirname
    cfg = ConfigParser()
    cfg.read(path.join(dirname, 'nicos.conf'))
    if cfg.has_option('nicos', 'setup_subdirs'):
        return tuple(path.join(path.dirname(dirname), subdir) for subdir in
                     cfg.get('nicos', 'setup_subdirs').split(','))
    else:
        return (dirname,)
