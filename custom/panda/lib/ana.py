#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, Attach, oneofdict, status
from nicos.devices.generic.axis import Axis
from nicos.devices.tango import AnalogOutput

ACTIONMODES = {0: 'alldown', 1: 'default', 2: 'dooropen', 3: 'service'}
R_ACTIONMODES = {'alldown': 0, 'default': 1, 'dooropen': 2, 'service': 3}


class AnaBlocks(AnalogOutput):
    parameters = {
        'actionmode':  Param('Block behavior',
                             type=oneofdict(ACTIONMODES),
                             default='default',
                             settable=True, volatile=True),
        'powertime':   Param('How long to power pushing down blocks', type=int,
                             settable=True, volatile=True),
        'windowsize':  Param('Window size', volatile=True, unit='deg'),
        'blockwidth':  Param('Block width', volatile=True, unit='deg'),
        'blockoffset': Param('Block offset', volatile=True, unit='deg'),
    }

    def doReadActionmode(self):
        return ACTIONMODES[self._dev.GetParam('Param200')]

    def doWriteActionmode(self, value):
        mode = R_ACTIONMODES[value]
        self._dev.SetParam([[mode], ['Param200']])

    def doReadPowertime(self):
        return self._dev.GetParam('Param204')

    def doWritePowertime(self, value):
        self._dev.SetParam([[value], ['Param204']])

    def doReadWindowsize(self):
        return self._dev.GetParam('Param201')

    def doReadBlockwidth(self):
        return self._dev.GetParam('Param202')

    def doReadBlockoffset(self):
        return self._dev.GetParam('Param203')


class ATT_Axis(Axis):
    attached_devices = {
        'anablocks': Attach('AnaBlocks device', AnaBlocks),
    }

    def _duringMoveAction(self, position):
        if self._attached_anablocks.status()[0] != status.BUSY:
            self._attached_anablocks.start(position)

    def _postMoveAction(self):
        self._attached_anablocks._hw_wait()
        self._attached_anablocks.start(self.read())

    def doReset(self):
        Axis.doReset(self)
        self._postMoveAction()
