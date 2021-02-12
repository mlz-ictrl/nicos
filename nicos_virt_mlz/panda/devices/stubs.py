#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Stubbed-out devices for VPANDA."""

from nicos.core import Moveable, Param, Readable, oneofdict, status
from nicos.devices.generic import VirtualMotor

from nicos_mlz.panda.devices.ana import ACTIONMODES


class Focibox(Readable):
    valuetype = str

    parameters = {
        'driverenable': Param('Simulated on-off', type=bool, settable=True),
    }

    def doRead(self, maxage=0):
        # for now, only one mono is supported in the simulation file.
        return 'PG'

    def comm(self, *args, **kwds):
        pass


class SatBoxInOut(Moveable):
    valuetype = int

    parameters = {
        'curvalue': Param('Current value', type=int, default=0, settable=True),
    }

    def doStart(self, target):
        self.curvalue = target

    def doRead(self, maxage=0):
        return self.curvalue

    def doStatus(self, maxage=0):
        return status.OK, ''


class AnaBlocks(Moveable):
    parameters = {
        'curvalue':    Param('Current value', default=0, settable=True),
        'actionmode':  Param('Block behavior',
                             type=oneofdict(ACTIONMODES),
                             default='default', settable=True),
        'powertime':   Param('How long to power pushing down blocks', type=int,
                             settable=True),
        'windowsize':  Param('Window size', unit='deg'),
        'blockwidth':  Param('Block width', unit='deg'),
        'blockoffset': Param('Block offset', unit='deg'),
    }

    def doStart(self, target):
        self.curvalue = target

    def doRead(self, maxage=0):
        return self.curvalue

    def doStatus(self, maxage=0):
        return status.OK, ''


class MccMotor(VirtualMotor):

    def _pushParams(self):
        pass
