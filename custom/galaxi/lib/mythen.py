#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Mythen detector"""

import numpy

from nicos.core import ArrayDesc, waitForStatus, status, usermethod, MASTER
from nicos.core.device import Measurable
from nicos.core.params import Param, dictof
from nicos.devices.tango import PyTangoDevice

P_TIME = 't'
P_FRAMES = 'f'

class MythenDetector(PyTangoDevice, Measurable):
    """Basic Tango device for Mythen detector."""

    STRSHAPE = ['x', 'y', 'z', 't']

    parameters = {
        'detshape':  Param('Shape of Mythen detector', type=dictof(str, int)),
        'energy':    Param('X-ray energy', type=float, unit='keV',
                           settable=True, volatile=True),
        'kthresh':   Param('Energy threshold', type=float, unit='keV',
                           settable=True, volatile=True),
        'frames':    Param('Number of frames within an acquisition', type=int,
                           settable=True, volatile = True),
        'time':      Param('Exposure time of one frame', type=int, unit='s',
                           settable=True, volatile = True),
        'remaining': Param('Remaining exposure time', type=int, unit='s',
                           volatile = True)
    }

    def doInit(self, mode):
        self.log.debug('Mythen detector init')
        self.arraydesc = ArrayDesc('data',
                                   (int(self.detshape['x']),
                                    int(self.detshape['t'])),
                                   numpy.uint32)
        if self._mode == MASTER:
            self._dev.Reset()
        self._t = self.time
        self._f = self.frames

    def presetInfo(self):
        return (P_TIME, P_FRAMES)

    def doSetPreset(self, **preset):
        self.log.debug('Mythen detector set preset')
        self._preset = preset
        if P_TIME in preset:
            self.doWriteTime(preset[P_TIME])
        if P_FRAMES in preset:
            self.doWriteFrames(preset[P_FRAMES])

    def doRead(self, maxage=0):
        self.log.debug('Mythen detector read')
        return self.lastfilename

    def doReadDetshape(self):
        ''' Method currently not implemented in server '''
        shvalue = self._dev.get_property('shape').values()[0]
        dshape = dict()
        for i in range(4):
            dshape[self.STRSHAPE[i]] = shvalue[i]
        return dshape

    def doReadEnergy(self):
        return self._dev.energy

    def doWriteEnergy(self, value):
        self._dev.energy = value

    def doReadKthresh(self):
        return self._dev.kthresh

    def doWriteKthresh(self, value):
        self._dev.kthresh = value

    def doReadFrames(self):
        return self._dev.frames

    def doWriteFrames(self, value):
        self._dev.frames = value

    def doReadTime(self):
        return self._dev.time

    def doWriteTime(self, value):
        self._dev.time = value

    def doReadRemaining(self):
        return self._dev.remainingTime

    def doStart(self):
        self.log.debug('Mythen detector wait for status')
        waitForStatus(self, ignore_errors=True)
        self.log.debug('Mythen detector start')
        self._dev.Start()

    def doStatus(self, maxage=0):
        if PyTangoDevice.doStatus(self, 0)[0] == status.BUSY:
            info ='Remaining exposure time:    ' + str(self.remaining) + ' s'
            return (status.BUSY, info)
        else:
            return PyTangoDevice.doStatus(self, 0)

    def doStop(self):
        self.log.debug('Mythen detector stop')
        self._dev.Stop()

    def doFinish(self):
        pass

    def doReset(self):
        self.log.debug('Mythen detector reset')
        self._dev.Reset()
        self._t = self.time
        self._f = self.frames

    @usermethod
    def sendCommand(self, command):
        """Send any command to Mythen"""
        return self._dev.SendCommand(command)

    @usermethod
    def getValueOf(self, parameter):
        """Request any parameter value from Mythen"""
        command = '-get ' + parameter
        self.sendCommand(command)

    def readFinalImage(self):
        """Returns oldest frame reshaped as 2D numpy array"""
        self.log.debug('Mythen detector read final image')
        return numpy.asarray(self._dev.value).reshape(int(self.detshape['x']),
                                                      int(self.detshape['t']))
