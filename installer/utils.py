#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
guidir = path.join(rootdir, 'nicos', 'clients', 'gui')

grrtdir = path.join(path.dirname(gr.__file__), 'bin')


# Make sure to generate the version file.
os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + path.pathsep + rootdir
subprocess.check_call([sys.executable,
                       path.join(rootdir, 'nicos', '_vendor', 'gitversion.py')])


# Include all modules/files for the facility directories.
def find_custom():
    res = []
    for facilityroot in glob.glob(path.join(rootdir, 'nicos_*')):
        for root, _dirs, files in os.walk(facilityroot):
            for fn in files:
                if fn.endswith('.pyc'):
                    continue
                res.append((path.join(root, fn), root[len(rootdir) + 1:]))
    return res


# Include all .ui files for the main GUI module.
def find_uis():
    res = []
    for root, _dirs, files in os.walk(guidir):
        if any(uifile for uifile in files if uifile.endswith('.ui')):
            res.append((path.join(root, '*.ui'),
                        path.join('nicos', 'clients', 'gui',
                                  root[len(guidir) + 1:])))
    return res


# Include the GR runtime.
def find_gr():
    return [
        (path.join(grrtdir, '*.*'), path.join('gr', 'bin')),
        (path.join(grrtdir, 'fonts', '*.*'), path.join('gr', 'bin', 'fonts')),
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
