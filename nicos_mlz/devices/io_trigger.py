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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""Special device for Sans1 Tisane triggering or mieze on Reseda/Mira"""

from nicos.core import Moveable, Override, Param, dictof, oneof, status
from nicos.devices.tango import PyTangoDevice


class Trigger(PyTangoDevice, Moveable):
    """sends a preconfigured string upon move to the configured StringIO

    This should only be used with SCPI devices and the string to be sent
    should *not* provoke an answer.
    """
    parameters = {
        'strings': Param('mapping of nicos-value to pre-configured string',
                         type=dictof(str, str), settable=True, unit=''),
        'safesetting': Param("selection of a 'safe' setting",
                             type=str, settable=True, unit=''),
    }
    parameter_overrides = {
        'unit' : Override(default='', mandatory=False),
    }

    def doInit(self, mode):
        self.valuetype = oneof(*self.strings.keys())
        if self.target not in self.strings:
            self._setROParam('target', self.safesetting)

    def doStart(self, target):
        # !ALWAYS! send selected string
        self._dev.WriteLine(self.strings[target])
        # wait until our buffer is empty
        self._dev.Flush()
        # send a query and wait for the response,
        # which will only come after the above string was fully processed
        # note: this relies on the fact that the selected string above will NOT
        # provoke an answer, but just set parameters (base it on the *LRN? output)
        self._dev.Communicate('SYST:ERROR?')

    def doStatus(self, maxage=0):
        return status.OK, 'indeterminate'

    def read(self, maxage=0):
        # fix bad overwrite from StringIO
        return Moveable.read(self, maxage)

    def doRead(self, maxage=0):
        # no way to read back!
        return self.target
