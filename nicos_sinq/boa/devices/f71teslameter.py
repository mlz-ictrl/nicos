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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************


from nicos.core import SIMULATION, Override, Param, Value, host
from nicos.core.device import Readable
from nicos.core.params import tupleof
from nicos.utils import closeSocket, parseHostPort, tcpSocket


class F71Teslameter(Readable):
    """
    At BOA they want to use a LakeShore F71 Teslameter. This class is for
    reading the data from it.
    """

    parameters = {
        'host':      Param('Hostname or IP and port',
                           type=host(defaultport=7777),
                           settable=True, mandatory=True),
    }

    parameter_overrides = {
            'unit': Override(volatile=True),
    }

    valuetype = tupleof(float, float, float, float)
    _connection = None
    _stream = None

    def doInit(self, mode):
        if mode != SIMULATION:
            try:
                self.doReset()
            except Exception:
                self.log.exception('Failed to connect to '
                                   'F71 Teslameter module')

    def doRead(self, maxage=0):
        self._stream.write('FETCh:DC? ALL \n')
        self._stream.flush()
        reply = self._stream.readline()
        r = reply.split(',')
        return tuple(float(n)*1000. for n in r)

    def valueInfo(self):
        return (
                Value(self.name + '.MAG', unit=self.unit),
                Value(self.name + '.X', unit=self.unit),
                Value(self.name + '.Y', unit=self.unit),
                Value(self.name + '.Z', unit=self.unit),
                )

    def doReset(self):
        if self._connection:
            closeSocket(self._connection)
        h, p = parseHostPort(self.host, 7777)
        self._connection = tcpSocket(h, p, timeout=1)
        self._stream = self._connection.makefile('rw', newline='\n')

    def doShutdown(self):
        if self._connection:
            closeSocket(self._connection)

    def doReadUnit(self):
        return 'mT'
