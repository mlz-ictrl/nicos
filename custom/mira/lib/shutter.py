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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for MIRA shutter readout/operation."""

import time

import IO

from nicos.core import usermethod, tacodev, Param, ModeError
from nicos.devices.taco.io import NamedDigitalInput
from nicos.core import SIMULATION, SLAVE


class Shutter(NamedDigitalInput):
    """
    Class for readout of the MIRA shutter via digital input card, and closing
    the shutter via digital output (tied into Pilz security system).
    """

    parameters = {
        'output': Param('The output for closing the shutter',
                        type=tacodev, mandatory=True),
    }

    def doInit(self, mode):
        NamedDigitalInput.doInit(self, mode)
        if mode != SIMULATION:
            self._outdev = self._create_client(self.output, IO.DigitalOutput)

    @usermethod
    def close(self):
        if self._mode == SLAVE:
            raise ModeError(self, 'closing shutter not allowed in slave mode')
        elif self._sim_active:
            return
        self._taco_guard(self._outdev.write, 1)
        time.sleep(0.5)
        self._taco_guard(self._outdev.write, 0)
        self.log.info('instrument shutter closed')
