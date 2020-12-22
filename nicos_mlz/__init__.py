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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""MLZ specific NICOS package."""

import socket
from os import path


def determine_instrument(setup_package_path):
    """MLZ specific way to find the NICOS instrument from the host name."""
    try:
        # Take the second part of the domain name (machine.instrument.frm2
        # or new-style machine.instrument.frm2.tum.de)
        hostparts = socket.getfqdn().split('.')
        instrument = hostparts[1].replace('-', '_')
        if instrument == 'jcns' and hostparts[0] == 'jcnsmon':
            instrument = 'jcnsmon'
    except (ValueError, IndexError, OSError):
        pass
    else:
        # ... but only if a subdir exists for it
        if path.isdir(path.join(setup_package_path, instrument)):
            return instrument
