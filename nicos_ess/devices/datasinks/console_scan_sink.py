# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
# *****************************************************************************
from nicos import session
from nicos.core import SIMULATION
from nicos.devices.datasinks.scan import \
    ConsoleScanSink as BaseConsoleScanSink, \
    ConsoleScanSinkHandler as BaseConsoleScanSinkHandler


class ConsoleScanSinkHandler(BaseConsoleScanSinkHandler):
    def prepare(self):
        if session.mode != SIMULATION:
            self.manager.assignCounter(self.dataset)


class ConsoleScanSink(BaseConsoleScanSink):
    """A DataSink that prints scan data onto the console."""
    handlerclass = ConsoleScanSinkHandler
