#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.devices.generic.axis import Axis as GenericAxis
from nicos.devices.vendor.ipc import IPCModBusTaco
from nicos.devices.taco.io import DigitalInput
from nicos.core import CommunicationError, Param

from TACOClient import TACOError
import TACOStates


class Axis(GenericAxis) :
    """ Refsans NOK Axis """

    attached_devices = {
        'bus'  : (IPCModBusTaco, 'IPC bus device'),
        'sll'  : (DigitalInput,  'Lower soft limit switch'),
        'shl'  : (DigitalInput,  'Upper soft limit switch'),
        'sref' : (DigitalInput,  'Reference switch'),
    }

    parameters = {
        'refpoint'    : Param('Reference position ',
                          type = float,
                          mandatory = True,
                         ),
    }

#   def doInit(self, mode) :
#       super(Axis, self).doInit(mode)

    def _movestep1(self, units) :
        """ Checks the current position of the axis and decides what's to do.
            If the new position is above the current it does nothing.
            Otherwise it tries to move to a position below the desired position.
            If this is not possibe it moves to the lower user limit.
            @param units desired position
        """
        if self.read() <= units:
            self.log.debug('movestep1 returns 0 -> new pos is above or equal current %f' % (units))
            return 0
        else:
            llimit = self.usermin
            try :
                if llimit > units or llimit > (units - self.backlash) :
                    self.motorstart(llimit)
                else:
                    self.motorstart(units - self.backlash)
            except TACOError:
                return 1
            return 0

    def _movestep2(self, units) :
        """
           This function moves the axis to the given position
           @param units
        """
        self.motorstart(units)
        # try :
        #     self.motorstart(units)
        # except TACOError, e:
        #     return 1
        return 0

    def motorstart(self, units ):
        self.log.debug('motorstart %f' % (units))
        if self.__readonly:
            self.log.error('motorstart %f BLOCKED' % (units))
        else:
            self._adevs['motor'].start(units)

    def readsteps(self) :
        """
           This method reads the current motor counter
        """
        try:
            return self._adevs['motor'].deviceQueryResource('counter')
        except TACOError:
            raise CommunicationError(self, 'Could not read steps')

    def printstatus(self, type = 'TACO') :
        if (type.upper() == 'TACO') :
            return self._adevs['motor']._dev.deviceStatus()
        elif (type.upper() == 'HIGH') :
            return self._adevs['shl'].read()
        elif (type.upper() == 'LOW') :
            return self._adevs['sll'].read()
        elif (type.upper() == 'REF') :
            return self._adevs['sref'].read()
        state = self._adevs['motor']._dev.deviceState()
        line = self._adevs['sref']._dev.deviceStatus()
        if state in [TACOStates.DEVICE_NORMAL, TACOStates.ON] :
            for i in ['sref', 'shl', 'shl'] :
                if self._adevs[i].read() :
                    line += ' %s: 1' % (i.upper())
        return line
