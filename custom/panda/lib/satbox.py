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
    _blades = [1, 2, 5, 10, 20]

    def doRead(self, maxage=0):
        inx = self._adevs['bus'].ReadBitsOutput(0x1020, len(self._blades))
        width = sum( [inx[i] * blade for i, blade in enumerate(self._blades)])
        #~ # currently the input bits dont work, since the magnetic field of the monoburg switches them all on
        #~ inx = self._adevs['bus'].ReadBitsInput(0x1000, 2*len(self._blades))
        #~ self.log.debug('position: %s' % inx)
        #~ width = 0
        #~ for i, blade in enumerate( self._blades):
            #~ if not inx[i*2]:
                #~ if inx[i*2+1]:
                    #~ width += blade
                #~ else:
                    #~ self.log.warning('%d mm blade in inconsistent state' % blade)
        return width

    def doStatus(self, maxage=0):
        #~ # currently the input bits dont work, since the magnetic field of the monoburg switches them all on		
        #~ inx = self._adevs['bus'].ReadBitsInput(0x1000, 2*len(self._blades))
        #~ for i, blade in enumerate( self._blades):
            #~ if inx[i*2] and inx[i*2+1]:
                #~ return status.BUSY, '%d mm blade moving' % blade
        return status.OK, ''

    def doStart(self, rpos):
        if rpos > sum(self._blades):
            raise InvalidValueError(self, 'Value %d too big!, maximum is %d' % (rpos,sum(self._blades)))
        which = [0] * len(self._blades)
        pos = rpos
        for i in xrange(len(self._blades)-1,-1,-1):
            blade = self._blades[i]
            if not blade:
                continue        # skip disabled (0 or None) blades
            if pos >= blade:
                which[i] = 1
                pos -= blade
        if pos != 0:
            self.log.warning('Value %d impossible, trying %d instead!'%(rpos,rpos+1))
            return self.doStart( rpos+1)
        self.log.debug('setting blades: %s' % [ which[i] * blade for i,blade in enumerate(which)])
        self._adevs['bus'].WriteBitsOutput(0x1020, which)
