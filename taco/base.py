#  -*- coding: iso-8859-15 -*-
# *****************************************************************************
# Module:
#   $Id $ 
#              
# Description:
#   NICOS TACO base classes
#
# Author:       
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   $Author $
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICOS-TACO base classes."""

__date__   = "$Date $"
__version__= "$Revision $"

import TACOStates
from TACOClient import TACOError

from nicm import status
from nicm.errors import CommunicationError, ProgrammingError


class TacoDevice(object):
    """Mixin class for TACO devices.

    Use it in concrete device classes like this:

        class Counter(TacoDevice, Countable):
            taco_class = IO.Counter

            # more overwritten methods

    i.e., put TacoDevice first in the base class list.
    """
    
    parameters = {
        'tacodevice': ('', True, 'TACO device name.'),
        'tacotimeout': (0, False, 'TACO client network timeout (in seconds).'),
        # the unit isn't mandatory -- TACO knows it already
        'unit': ('', False, 'Unit of the device main value.'),
    }

    # the TACO client class to instantiate
    taco_class = None
    # whether to call deviceReset() if the initial switch-on fails
    taco_resetok = True

    def doInit(self):
        if self.taco_class is None:
            raise ProgrammingError('missing taco_class attribute in class '
                                   + self.__class__.__name__)
        
        devname = self.getTacodevice()
        try:
            self._dev = self.taco_class(devname)
        except TACOError, err:
            raise CommunicationError(
                'Could not connect to TACO device %r, TACO error: %d; %s' %
                (devname, err.errcode, err))

        try:
            timeout = self.getTacotimeout()
            if timeout != 0:
                self._dev.setClientNetworkTimeout(timeout)
        except TACOError, err:
            self.printwarning('Setting TACO network timeout failed: %d; %s' %
                              (err.errcode, err))

        try:
            self._dev.deviceOn()
        except TACOError, err:
            self.printwarning('Switching TACO device %r on failed: %d; %s' %
                              (devname, err.errcode, err))
            try:
                if self._dev.deviceState() == TACOStates.FAULT:
                    if self.taco_resetok:
                        self._dev.deviceReset()
                self._dev.deviceOn()
            except TACOError, err:
                raise CommunicationError(
                    'Switching TACO device %r on after reset failed: %d; %s' %
                    (devname, err.errcode, err))

    def doRead(self):
        return self._dev.read()

    def doStatus(self):
        # this needs to be device-defined
        return status.UNKNOWN

    def doReset(self):
        self._dev.deviceReset()

    def doGetUnit(self):
        return self._dev.unit()
