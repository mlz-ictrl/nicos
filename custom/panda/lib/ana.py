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

"""Analysator stuff for PANDA"""

__version__ = "$Revision$"

from time import sleep, time as currenttime

from nicos.core import status, intrange, oneof, anytype, Device, Param, \
     Readable, Moveable, NicosError, ProgrammingError, TimeoutError, tacodev, usermethod
from nicos.generic.axis import Axis

from IO import DigitalOutput


class ATT_Axis(Axis):

    parameters = {
        'blockdevice1': Param('First i7000', type=tacodev, mandatory=True),
        'blockdevice2': Param('Second i7000', type=tacodev, mandatory=True),
        'blockdevice3': Param('Third i7000', type=tacodev, mandatory=True),
        'windowsize': Param('Window size', default=11.5, unit='deg'),
        'blockwidth': Param('Block width', default=15.12, unit='deg'),
        'blockoffset': Param('Block offset', default=-7.7, unit='deg'),
    }
    
    def doInit(self):
        Axis.doInit(self)
        if self._mode != 'simulation':
            self._dev1 = DigitalOutput(self.blockdevice1)
            self._dev2 = DigitalOutput(self.blockdevice2)
            self._dev3 = DigitalOutput(self.blockdevice3)
            try:
                self._dev1.deviceOn()
                self._dev2.deviceOn()
                self._dev3.deviceOn()
            except Exception:
                self.log.warning('could not switch on taco devices', exc=1)
    
    def _duringMoveAction(self, position):
        self._move_blocks(position)
        
    def _postMoveAction(self):
        self._move_blocks(self.read())
        
    def doReset(self):
        Axis.doReset(self)
        self._move_blocks(self.read())
        
    def _move_blocks(self, pos):
        # calculate new block positions
        templist = [0,0,0]
        uwl=pos+self.windowsize/2.0   
        lwl=pos-self.windowsize/2.0   
        mask=0
        for j in range(18):
            index=j
            module=0
            while index>7:
                    index-=8
                    module+=1
            lbl=self.blockwidth*(8-j)+self.blockoffset
            ubl=self.blockwidth*(9-j)+self.blockoffset
            blockup=0
            if ubl >= lwl:  # block is not left to window
                if lbl <= uwl:  # block is not right to window
                    blockup=1
            if blockup==1:
                templist[module] +=(1 << (index)) 
        self._dev1.write(templist[0])
        self._dev2.write(templist[1])
        self._dev3.write(templist[2])

    @usermethod
    def allblocksdown(self):
        self._dev1.write(0)
        self._dev2.write(0)
        self._dev3.write(0)

    @usermethod
    def doorblocksup(self):
        self._dev1.write(63)

    @usermethod
    def doorblocksdown(self):
        self._dev1.write(0)

    @usermethod
    def allblocksup(self):
        self._dev1.write(255)
        self._dev2.write(255)
        self._dev3.write(3)

    @usermethod
    def printstatusinfo(self):
        self.log.info('blocks up: %018b' % (self._dev1.read() +
                                    self._dev2.read() << 8 +
                                    self._dev3.read() << 16))

    