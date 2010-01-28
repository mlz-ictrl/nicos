#  -*- coding: iso-8859-15 -*-
# *****************************************************************************
# Module:
#   $Id$ 
#              
# Description:
#   NICOS TACO motor definition
#
# Author:       
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   $Author$
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

""" implementation of the class for TACO controlled motors """

__author__ = "Jens Krüger <jens.krueger@frm2.tum.de>"
__date__   = "$Date$"
__version__= "$Revision$"

from Motor import Motor as TACOMotor
import TACOStates
import TACOClient

from nicm import status
from nicm.errors import ConfigurationError, NicmError
from nicm.motor import Motor as NicmMotor

class Motor(NicmMotor):

    parameters = {
        'tacodevice': ('', True, 'TACO device name.'),
    }

    def doVersion(self):
        """ returns the version of the module (class)"""
        return __version__

    def doInit(self):
        try :
	    self._dev = TACOMotor(self.getTacodevice())
        except TACOClient.TACOError, e:
            self.printerror()
            raise CommunicationError("TACO Motor device '%s' not available\nTACO error code: %d ; %s " % (self.getTacodevice(), e.errcode, e), 0)
        except Exception, e:
            self.printerror()
            raise e

        try:
            self._dev.deviceOn()
        except TACOClient.TACOError,e:
            self.printerror()
            try:
                if self._dev.deviceState() == TACOStates.FAULT :
                    self._dev.deviceReset()
                self._dev.deviceOn()
            except TACOClient.TACOError,e:
                raise CommunicationError("TACOError: %d; Cannot switch on Motor device : '%s'\n%s " % (e.errcode, self._dev.deviceName(), e), 0)
            except Exception, e:
                self.printerror()
                raise CommunicationError("Unexpected error occured: %s: " % (sys.exc_info()[0]), 0)
        self.doSetUnit(self._dev.unit())

    def doStart(self, target) :
        try :
            self._dev.start(target)
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doRead(self) :
        try :
            return self._dev.read()
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doSetPosition(self, target) :
        try :
            self._dev.setpos(target)
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doStatus(self) :
        try :
            stat = self._dev.deviceState()
            if stat == TACOStates.DEVICE_NORMAL : 
                return status.OK
            elif stat == TACOStates.MOVING :
                return status.BUSY
            else :
                return status.ERROR
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doReset(self) :
        try :
            self._dev.deviceReset()
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doStop(self) :
        try :
            self._dev.stop()
        except TACOClient.TACOError, e :
            self.printerror()
            raise e

    def doGetUnit(self) :
        try :
            return self._dev.unit()
        except TACOClient.TACOError, e :
            self.printerror()
            raise e
     
#    def doGetTacodevice(self) :
#        return self._params['tacodevice']
