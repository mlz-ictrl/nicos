# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""NICOS device for the Bruker OPUS Tango server."""

from nicos.core import Measurable, Value
from nicos.devices.tango import PyTangoDevice


class OpusChannel(PyTangoDevice, Measurable):
    """Trigger an FTIR measurement and return the resulting file name."""

    def presetInfo(self):
        return ()

    def doSetPreset(self, **_preset):
        # The OPUS Tango device has no supported preselection right now.
        pass

    def doPrepare(self):
        self._dev.Clear()
        self._dev.Prepare()

    def doStart(self):
        self._dev.Start()

    def doStop(self):
        # The Tango server currently cannot abort an OPUS measurement, but
        # forwarding Stop keeps this device compatible if that changes.
        self._dev.Stop()

    def doFinish(self):
        self._dev.Stop()

    def doRead(self, maxage=0):
        return self._dev.value

    def valueInfo(self):
        return Value(self.name, type='filename', fmtstr='%s'),
