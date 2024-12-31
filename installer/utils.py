# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

import glob
import os
import subprocess
import sys
from os import path

import gr

rootdir = path.abspath('..')
guidirs = [path.join('nicos', 'clients', 'gui'),
           path.join('nicos', 'clients', 'flowui')]

# Make sure to generate the version file.
os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + path.pathsep + rootdir
subprocess.check_call([sys.executable,
                       path.join(rootdir, 'nicos', '_vendor', 'gitversion.py')])


# Include all modules/files for the facility directories.
def find_custom():
    res = []
    for facilityroot in glob.glob(path.join(rootdir, 'nicos_*')):
        for root, dirs, files in os.walk(facilityroot):
            # Prune unneeded subdirs.
            dirs[:] = [d for d in dirs
                       if d not in ('setups', 'testscripts', 'template')]
            for fn in files:
                if fn.endswith('.pyc'):
                    continue
                res.append((path.join(root, fn), root[len(rootdir) + 1:]))
    return res

# find resource files
def find_resources():
    res = []
    for root, _dirs, files in os.walk(path.join(rootdir,  'resources')):
        targetdir = root[len(rootdir) + 1:]
        for fn in files:
            res.append((path.join(root, fn), targetdir))
    res.append((path.join(rootdir,'nicos/clients/flowui/guiconfig.qss'), 'nicos/clients/flowui'))
    return res

# Include all .ui files for the main GUI module.
def find_uis():
    res = []
    for guidir in guidirs:
        for root, _dirs, files in os.walk(path.join(rootdir, guidir)):
            if any(uifile for uifile in files if uifile.endswith('.ui')):
                res.append((path.join(root, '*.ui'),
                            path.join(guidir,
                                      root[len(path.join(rootdir, guidir)) + 1:])))
    return res


# Include the GR runtime.
def find_gr():
    grrtdir = path.join(path.dirname(gr.__file__), 'bin')
    return [
        (path.join(grrtdir, '*.*'), path.join('gr', 'bin')),
        (path.join(grrtdir, '..', 'fonts', '*.*'), path.join('gr', 'fonts')),
    ]

def find_gr_osx():
    grrtdir = path.join(path.dirname(gr.__file__), 'lib')
    return [
        (path.join(grrtdir, '*.*'), path.join('gr', 'lib')),
        (path.join(grrtdir, '..', 'fonts', '*.*'), path.join('gr', 'fonts')),
    ]


# Include all modules found in a certain package -- they may not be
# automatically found because of dynamic importing via the guiconfig file
# and custom widgets in .ui files.
def find_modules(*modules):
    res = []
    startdir = path.join(rootdir, *modules)
    startmod = '.'.join(modules) + '.'
    for root, _dirs, files in os.walk(startdir):
        modpath = root[len(startdir) + 1:].replace(path.sep, '.')
        if modpath:
            modpath += '.'
        for mod in files:
            if mod.endswith('.py'):
                res.append(startmod + modpath + mod[:-3])
    return res
