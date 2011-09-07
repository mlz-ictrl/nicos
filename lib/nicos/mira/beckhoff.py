#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Devices for the Beckhoff Busklemmensystem."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from Modbus import Modbus

from nicos.io import DigitalOutput
from nicos.device import Param


class BeckhoffDigitalOutput(DigitalOutput):
    """
    Device object for a Varian Mini-Task (AG81 type) pump.
    """
    taco_class = Modbus

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
        'bitwidth': Param('Number of bits to switch', type=int,
                          mandatory=True),
    }

    def doInit(self):
        DigitalOutput.doInit(self)
        # switch off watchdog, important before doing any write access
        if self._mode != 'simulation':
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self):
        return tuple(self._taco_guard(self._dev.readCoils, (0,
                                      self.startoffset, self.bitwidth)))

    def doStart(self, value):
        self._taco_guard(self._dev.writeMultipleCoils, (0,
                         self.startoffset) + tuple(value))

    def doIsAllowed(self, target):
        try:
            if len(target) != self.bitwidth:
                return False, ('value needs to be a sequence of length %d, '
                               'not %r' % (self.bitwidth, target))
        except TypeError:
            return False, 'invalid value for device: %r' % target
        return True, ''

    def doReadFmtstr(self):
        return '{ ' + ' '.join(['%s'] * self.bitwidth) + ' }'
