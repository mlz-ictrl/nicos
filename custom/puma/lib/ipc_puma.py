#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""PUMA specific modifications to NICOS's module for IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

from time import sleep

from nicos.core import Override, waitForStatus
from nicos.devices.vendor.ipc import Coder as IPCCoder, Motor as IPCMotor, SlitMotor as IPCSlitMotor


class Coder(IPCCoder):
    """Same as vendor.ipc.Coder but don't write the config byte
    """
    parameter_overrides = {
        'confbyte' : Override(settable = False),
    }

    def doWriteConfbyte(self, byte):
        self.log.warning('Config byte can\'t be changed like this.')
#        self._adevs['bus'].send(self.addr, 154, byte, 3)
        return


class Motor(IPCMotor):
    """Same as vendor.ipc.Motor but don't write the config byte

    also supply a custom doWait which sleeps before doing the same
    as the normal wait would do.
    """
    parameter_overrides = {
        'confbyte' : Override(settable = False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        return
 #       if self._hwtype == 'single':
 #           self._adevs['bus'].send(self.addr, 49, value, 3)
 #       else:
 #           raise InvalidValueError(self, 'confbyte not supported by card')
 #       self.log.info('parameter change not permanent, use _store() '
 #                     'method to write to EEPROM')

    def doWait(self):
        sleep(0.1)
        waitForStatus(self, 0.2, errorstates=())


class SlitMotor(IPCSlitMotor):
    """Same as vendor.ipc.SlitMotor with custom doWait,

    This doWait uses a different delay between status polls.
    The reason is unknown.
    """

    def doWait(self):
        waitForStatus(self, max(0.3, self.timeout / 10.5), errorstates=())
