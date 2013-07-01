#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
The nicos package contains all standard NICOS commands and devices.
"""

__version__   = "$Revision$"
nicos_version = "2.4.0-dev"

import os
import new
import sys
from os import path
import distutils.util

# Check for Python version 2.6+.
if sys.version_info[:2] < (2, 6):
    raise ImportError('NICOS requires Python 2.6 or higher')

# Add instrument-specific directories to the package path.
pkgpath = path.join(path.dirname(__file__), '..', '..', 'custom')
if path.isdir(pkgpath):
    for subdir in os.listdir(pkgpath):
        mod = sys.modules['nicos.' + subdir] = new.module('nicos.' + subdir)
        mod.__path__ = [path.join(pkgpath, subdir, 'lib')]
        globals()[subdir] = mod

# Add platform-specific directories (lib/plat-PLATFORM)
sys.path.append(path.join(path.dirname(__file__), '..',
                          'plat-%s' % distutils.util.get_platform()))

# Create the nicos session object here to allow the import of submodules.
# The real class is set later.

class Session(object):
    pass
session = Session()


# Read config file and set environment variables.

from nicos.utils import readConfig
readConfig()
