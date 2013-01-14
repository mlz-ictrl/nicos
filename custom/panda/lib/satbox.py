#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""PANDA's Attenuator controling device for NICOS."""

__version__ = "$Revision$"

#from nicos.core import *
from nicos.core import status, InvalidValueError, Moveable
from nicos.panda.wechsler import Beckhoff

class SatBox(Moveable):
    attached_devices = {
        'bus': (Beckhoff, 'modbus'),
    }

    valuetype = int
    _widths = [1, 2, 5, 10, 20]

    def doRead(self, maxage=0):
        inx = self._adevs['bus'].ReadBitsOutput(0x1020, len(self._widths))
        return sum([inx[i]*self._widths[i] for i in range(len(self._widths))])

        #~ # currently the input bits dont work, since the magnetic field of the monoburg switches them all on
        #~ inx = self._adevs['bus'].ReadBitsInput(0x1000, 10)
        #~ self.log.debug('position: %s' % inx)
        #~ width = 0
    def doStatus(self, maxage=0):
        return status.OK, ''
        #~ in1 = self._adevs['bus'].ReadBitsInput(0x1000, 8)
        #~ in2 = self._adevs['bus'].ReadBitsInput(0x1008, 2)
        #~ inx = in1 + in2
        #~ for i in range(5):
            #~ if inx[i*2] and inx[i*2+1]:
                #~ return status.BUSY, '%d mm blade moving' % self._widths[i]
        #~ return status.OK, ''

    def doStart(self, rpos):
        if rpos > sum(self._widths):
            raise InvalidValueError(self, 'Value %d too big!, maximum is %d' % (rpos,sum(self._widths)))
        which = [0] * len(self._widths)
        pos = rpos
        for i in range(len(self._widths)-1,-1,-1):
            if pos >= self._widths[i]:
                which[i] = 1
                pos -= self._widths[i]
        if pos != 0:
            self.log.warning('Value %d impossible, trying %d instead!'%(rpos,rpos+1))
            return self.doStart( rpos+1)
        self.log.debug('setting blades: %s' % [which[i]*self._widths[i] for i in range(len(which))])
        self._adevs['bus'].WriteBitsOutput(0x1020, which)
