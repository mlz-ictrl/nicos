#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Temporary package to ease transition to the new custom namespace layout."""

import os
import sys
import types
from os import path

from nicos.configmod import config

pkgpath = config.custom_path
if path.isdir(pkgpath):
    for subdir in os.listdir(pkgpath):
        # create a "nicos_mlz.instrumentname" parent module
        newmod = sys.modules['nicos_mlz.' + subdir] = \
            types.ModuleType('nicos_mlz.' + subdir)
        newmod.__path__ = [path.join(pkgpath, subdir, 'lib')]
        globals()[subdir] = newmod

        # import old module under the name "devices"
        devmod = sys.modules['nicos_mlz.' + subdir + '.devices'] = \
            types.ModuleType('nicos_mlz.' + subdir + '.devices')
        devmod.__path__ = [path.join(pkgpath, subdir, 'lib')]
        newmod.devices = devmod

        # and the gui subdir under the name "gui"
        guimod = sys.modules['nicos_mlz.' + subdir + '.gui'] = \
            types.ModuleType('nicos_mlz.' + subdir + '.gui')
        guimod.__path__ = [path.join(pkgpath, subdir, 'lib', 'gui')]
        newmod.devices = guimod
