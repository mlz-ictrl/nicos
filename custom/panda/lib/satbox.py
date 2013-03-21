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
from nicos.core import status, InvalidValueError, Moveable, Param, convdoc, floatrange
from nicos.panda.wechsler import Beckhoff

from Modbus import Modbus

from nicos.devices.taco import TacoDevice

class positive_float(object):
    ''' Checker for floats >= 0'''

    def __init__(self):
        self.__doc__ = 'a float >=0'

    def __call__(self, val=None):
        if val is None:
            return 0.
        val = float(val)
        if not val >= 0:
            raise ValueError('value needs to be >= 0')
        return val

class checkedlist(list):
    def __init__(self, conv, *args):
        self._conv=conv
        list.__init__(self,*args)
    def __setitem__(self, idx, val):
        list.__setitem__(self, idx, self._conv(val))
    def append(self, what):
        list.append(self, self._conv(what))
    def extend(self,l):
        for v in l:
            self.append(l)
    def insert(self, idx, val):
        list.insert(self, idx, self._conv(val))

class checkedlistof(object):
    def __init__(self, conv):
        self.__doc__ = 'a list of %s' % convdoc(conv)
        self.conv = conv

    def __call__(self, val=None):
        val = val if val is not None else list()
        if not isinstance(val, list):
            raise ValueError('value needs to be a list')
        return checkedlist(self.conv,map(self.conv, val))

class SatBox(TacoDevice, Moveable):
    """
    Device Object for PANDA's Attenuator, controlled by a WUT-device via a ModBusTCP interface.
    """
    taco_class = Modbus

    valuetype = int

    parameters = {
        'blades': Param('Thickness of the blades, starting with lowest bit',
                         type=checkedlistof(floatrange(0,1000)), mandatory=True),
        'slave_addr': Param('Modbus-slave-addr (Beckhoff=0,WUT=1)',
                       type=int,mandatory=True),
        'addr_out': Param('Base Address for activating Coils',
                           type=int, mandatory=True),
        #~ 'addr_in': Param('Base Address for reading switches giving real blade state',
                           #~ type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != 'simulation':
            if self.slave_addr == 0: # only disable Watchdog for Beckhoff!
                self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        # just read back the OUTPUT values, scale with bladethickness and sum up
        return sum(b*r for b, r in zip(self.blades,
                    self._taco_guard(
                        self._dev.readCoils, (self.slave_addr, self.addr_out, len(self.blades))))
                    )

    def doStart(self, rpos):
        if rpos > sum(self.blades):
            raise InvalidValueError(self, 'Value %d too big!, maximum is %d'
                                            % (rpos, sum(self.blades))
        which = [0] * len(self.blades)
        pos = rpos
        # start with biggest blade and work downwards, ignoring disabled blades
        for i, bladewidth in reversed(enumerate(self.blades)):
            if bladewidth and pos >= bladewidth:
                which[i] = 1
                pos -= bladewidth
        if pos != 0:
            self.log.warning('Value %d impossible, trying %d instead!' %
                             (rpos, rpos + 1))
            return self.doStart(rpos + 1)
        self.log.debug('setting blades: %s' %
                       [s * b for s, b in zip(which, self.blades)]
                      )
        self._taco_guard(self._dev.writeMultipleCoils, (self.slave_addr,
                         self.addr_out) + tuple(which))

    def doIsAllowed(self, target):
        if not (0<=target<=self._blades_sum):
            return False, 'Value outside range 0..%d'%self._blades_sum
        if int(target) != target:
            return False, 'Value must be an integer !'
        return True, ''

