# -*- coding: utf-8 -*-
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Mythen detector"""

import numpy
import time
from nicos.core import waitForStatus, status, usermethod, MASTER, Value
from nicos.core.params import Param, ArrayDesc
from nicos.devices.tango import PyTangoDevice
from nicos.core.constants import FINAL, INTERRUPTED
from nicos.devices.generic.detector import TimerChannelMixin, ImageChannelMixin,\
    ActiveChannel, Detector

P_TIME = 't'
P_FRAMES = 'f'

DATASIZE = 1280


class MythenTimer(PyTangoDevice, TimerChannelMixin, ActiveChannel):
    """
    Timer channel for Mythen detector
    """
    parameters = {
        '_starttime':   Param('Cached counting start time',
                              type=float, default=0, settable=False,
                              userparam=False),
        '_stoptime':    Param('Cached counting stop time',
                              type=float, settable=False, userparam=False),
    }

    def doInit(self, mode):
        self._setROParam('_stoptime', time.time())

    def doRead(self, maxage=0):
        if self._stoptime:
            return [min(self._stoptime - self._starttime,
                        self.preselection)]
        return [round((time.time() - self._starttime), 3)]

    def valueInfo(self):
        return (Value(name='time', fmtstr='%.2f'),)

    def doStart(self):
        self._setROParam('_starttime', time.time())
        self._setROParam('_stoptime', 0)

    def doFinish(self):
        self._setROParam('_stoptime', time.time())

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        return PyTangoDevice.doStatus(self, 0)


class MythenImage(PyTangoDevice, ImageChannelMixin, ActiveChannel):
    """Basic Tango device for Mythen detector."""

    parameters = {
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
        self.arraydesc = ArrayDesc('data', (self.frames, DATASIZE), numpy.uint32)
        if self._mode == MASTER:
            self._dev.Reset()
            self.preselection = float(self.time)

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
        self.arraydesc = ArrayDesc('data', (self.frames, DATASIZE), numpy.uint32)

    def doReadTime(self):
        return self._dev.time

    def doWriteTime(self, value):
        self._dev.time = value
        self.preselection = value

    def doReadRemaining(self):
        return self._dev.remainingTime

    def doStart(self):
        self.log.debug('Mythen detector wait for status')
        waitForStatus(self, ignore_errors=True)
        self.readresult = [0]
        self.log.debug('Mythen detector start')
        self._dev.Start()

    def doStatus(self, maxage=0):
        if PyTangoDevice.doStatus(self, 0)[0] == status.BUSY:
            info = 'Remaining exposure time:    ' + str(self.remaining) + ' s'
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

    @usermethod
    def sendCommand(self, command):
        """Send any command to Mythen"""
        return self._dev.SendCommand(command)

    @usermethod
    def getValueOf(self, parameter):
        """Request any parameter value from Mythen"""
        command = '-get ' + parameter
        self.sendCommand(command)

    def valueInfo(self):
        return tuple(Value('frame-%d' % i, fmtstr='%d')
                     for i in range(1, self.frames + 1))

    def doReadArray(self, quality):
        """Returns all frames reshaped as 2D numpy array"""
        if quality in (FINAL, INTERRUPTED):
            self.log.debug('Mythen detector read final image')
            arr = numpy.asarray(self._dev.value, numpy.uint32)
            shape = self.arraydesc.shape
            arr = arr.reshape(shape)
            self.readresult = list(arr.sum(axis=1))
            return arr
        return None


class MythenDetector(Detector):
    """Mythen detector"""

    def presetInfo(self):
        presets = Detector.presetInfo(self)
        presets.update((P_TIME, P_FRAMES))
        return presets

    def doSetPreset(self, **preset):
        self.log.debug('Mythen detector set preset')
        myimage = self._attached_images[0]
        if P_TIME in preset:
            myimage.doWriteTime(preset[P_TIME])
            new_preset = {P_TIME: preset[P_TIME]}
            Detector.doSetPreset(self, **new_preset)
        if P_FRAMES in preset:
            myimage.doWriteFrames(preset[P_FRAMES])
