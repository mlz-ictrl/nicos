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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""SINQ specific NICOS package."""

from __future__ import absolute_import

import socket
from os import path


def determine_instrument(setup_package_path):
    """SINQ specific way to find the NICOS instrument from the host name."""
    try:
        domain = 'nicos_sinq/' + socket.getfqdn()
    except (ValueError, IndexError, socket.error):
        pass
    else:
        # ... but only if a subdir exists for it
        if path.isdir(path.join(setup_package_path, domain)):
            return domain.replace('/', '.')
