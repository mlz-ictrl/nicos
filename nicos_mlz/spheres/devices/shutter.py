#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

"""
Device related to the shutter at SPHERES
"""

from __future__ import absolute_import, division, print_function

from nicos.core import status
from nicos.core.mixins import HasTimeout
from nicos.core.params import Attach, Param
from nicos.devices.tango import NamedDigitalInput, NamedDigitalOutput


class ShutterCluster(HasTimeout, NamedDigitalOutput):
    '''
    Combines the state of different shutters to one overall state.
    Always displays closed if the instrument shutter is closed.
    State is set to warning if the instrument shutter is open,
    but upstream shutters are closed.
    Status messages are set in the setup.
    '''

    CLOSED = 'closed'
    UPSTREAMCLOSED = 'upstream closed'
    DOOROPEN = 'closed but door open'
    CHAINOPEN = 'closed but chain open'
    CLOSEDSTATES = [CLOSED, UPSTREAMCLOSED]

    attached_devices = {
        'upstream':
            Attach('upstreamshutters',
                   NamedDigitalInput,
                   multiple=True),
        'chains':
            Attach('housingchains',
                   NamedDigitalInput,
                   multiple=True),
        'door':
            Attach('door', NamedDigitalInput)
    }

    parameters = {
        'mapping':
            Param('Mapping for the shutter values',
                  type=dict),
        'chainstatemapping':
            Param('Mapping for the chain status',
                  type=dict),
        'shutterstatemapping':
            Param('Mapping for the shutter status',
                  type=dict),
        'attachedmapping':
            Param('Mapping for incoming values of the attached devices',
                  type=dict),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)

        # just in case the statusmapping is reversed in the setup
        self._shuttermapping = dict((v, k)
                                    for (k, v) in self.shutterstatemapping.items())
        self._shuttermapping.update(self.shutterstatemapping)

        self._chainmapping = dict((v, k)
                                  for (k, v) in self.chainstatemapping.items())
        self._chainmapping.update(self.chainstatemapping)

        # 'constant' for comparison if all the shutters are open
        self._allUpstreamOpen = 2**len(self._attached_upstream)-1

    def getCurrentShutterState(self):
        upstreamstate = 0
        for i, shutter in enumerate(self._attached_upstream):
            upstreamstate += self.attachedmapping[shutter.read()] << i

        instrumentstate = self._dev.value

        return upstreamstate, instrumentstate

    def getCurrentChainState(self):
        chainstate = 0
        for i, chain in enumerate(self._attached_chains):
            chainstate += self.attachedmapping[chain.read()] << i

        return chainstate

    def doRead(self, maxage=0):
        upstream, instrument = self.getCurrentShutterState()

        if not instrument:
            # upstream state doesn't matter if the instrument shutter is closed
            return self.CLOSED
        elif upstream < self._allUpstreamOpen:
            return self.UPSTREAMCLOSED

        return 'open'

    def doStatus(self, maxage=0):
        upstream, instrument = self.getCurrentShutterState()
        chains = self.getCurrentChainState()

        if instrument:
            if upstream == self._allUpstreamOpen:
                return status.OK, ''
        else:
            if self._attached_door.read() != 'yes':
                return status.WARN, 'door open'
            elif not chains:
                return status.OK, 'shutter closed'
            return status.WARN, self._chainmapping[chains]

        return status.WARN, self._shuttermapping[upstream]

    def doReset(self):
        NamedDigitalOutput.doReset(self)
        self.move('closed')
