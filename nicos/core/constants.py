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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS core constants."""

# session modes
MASTER = 'master'
SLAVE = 'slave'
SIMULATION = 'simulation'
MAINTENANCE = 'maintenance'

# session types
MAIN = 'main'
POLLER = 'poller'

# data qualities
LIVE = 'live'
INTERMEDIATE = 'intermediate'
FINAL = 'final'
INTERRUPTED = 'interrupted'

# data sink types
UNKNOWN = 'unknown'
SCAN = 'scan'
SUBSCAN = 'subscan'
POINT = 'point'
BLOCK = 'block'

# data display
NOT_AVAILABLE = 'n/a'

# live data
FILE = 'file'