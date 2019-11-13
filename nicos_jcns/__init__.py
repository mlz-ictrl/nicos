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

"""JCNS lab/infrastructure specific NICOS package."""

from __future__ import absolute_import, division, print_function

import socket
from os import path


def determine_instrument(setup_package_path):
    """JCNS lab and infrastructure way to find the instrument."""
    try:
        hostname = socket.gethostname().split('.')
        if hostname[1] in ('fourcircle', 'galaxi'):
            domain = hostname[1]
        else:
            domain = hostname[0]
    except (ValueError, IndexError, socket.error):
        pass
    else:
        # ... but only if a subdir exists for it
        if path.isdir(path.join(setup_package_path, domain)):
            return domain
