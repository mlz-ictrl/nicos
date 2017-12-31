#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

import sys
from logging import getLogger

# Provide the config object.
from nicos.configmod import config

# Determine our version(s).
from nicos._vendor.gitversion import get_nicos_version, get_git_version
__version__ = nicos_version = get_nicos_version()

# Check for Python version 2.7+ or 3.3+.
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    raise ImportError('NICOS requires Python 2.7 or higher')
elif sys.version_info[0] == 3 and sys.version_info[1] < 3:
    raise ImportError('NICOS requires Python 3.3 or higher')


# Create the nicos session object here to allow the import of submodules.
# The real class is set later.
class Session(object):
    log = getLogger('Nicos early logger')


session = Session()


def get_custom_version():
    return get_git_version(cwd=config.setup_package_path)
