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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

"""Module to implement generic sinq detector and ControlDetector
"""

from __future__ import absolute_import, division, print_function

from nicos.core import Attach, Measurable
from nicos.devices.generic import Detector
from nicos.utils import uniq

from nicos_ess.devices.epics.detector import EpicsCounterActiveChannel, \
    EpicsTimerActiveChannel
from nicos_sinq.devices.epics.scaler_record import EpicsScalerRecord


class SinqDetector(EpicsScalerRecord):
    """Custom detector for SINQ.

    Only time and monitor presets are present.
    """

    attached_devices = {
        'timepreset': Attach('Device to set the preset time',
                             EpicsTimerActiveChannel),
        'monitorpreset': Attach('Device to set the monitor preset',
                                EpicsCounterActiveChannel)
    }

    monitor_preset_names = ['m', 'monitor']
    time_preset_names = ['t', 'time']

    def _presetiter(self):
        for name in self.monitor_preset_names:
            yield name, self._attached_monitorpreset, 'monitor'
        for name in self.time_preset_names:
            yield name, self._attached_timepreset, 'time'

    def _getMasters(self):
        self._channels = uniq(self._channels + [self._attached_monitorpreset,
                                                self._attached_timepreset])
        EpicsScalerRecord._getMasters(self)

    def doSetPreset(self, **preset):
        # The counter box can set one time and count preset. If the time
        # preset is set, auto set the count preset to 0 and vice-a-versa.
        # Both presets cannot be set at a time.

        # This represents the various possible count and time presets
        countpreset = set(preset).intersection(self.monitor_preset_names)
        timepreset = set(preset).intersection(self.time_preset_names)

        # Check if user set both time and count preset
        if countpreset and timepreset:
            self.log.debug('Both count and time preset cannot be set at '
                           'the same time.')
            self.log.debug('Using just the count preset.')
            for name in timepreset:
                preset.pop(name)
            timepreset = set()

        if timepreset:
            preset['m'] = 0
            self.log.debug('Setting time preset of %f',
                           preset[timepreset.pop()])
            self.log.debug('Also updating the count preset to 0')

        if countpreset:
            preset['t'] = 0
            self.log.debug('Setting count preset of %d',
                           preset[countpreset.pop()])
            self.log.debug('Also updating the time preset to 0')

        # Let the parent handle the rest
        EpicsScalerRecord.doSetPreset(self, **preset)

    def doInfo(self):
        ret = EpicsScalerRecord.doInfo(self)

        # Check for the mode and preset
        mode = ''
        value = 0
        unit = ''
        for d in self._masters:
            for k in self._presetkeys:
                if self._presetkeys[k] and\
                        self._presetkeys[k][0].name == d.name:
                    preselection = d.preselection
                    if preselection != 0:
                        value = preselection
                        unit = d.unit
                        mode = 'timer' if k.startswith('t') else 'monitor'
                        break
        ret.append(('mode', mode, mode, '', 'presets'))
        ret.append(('preset', value, '%s' % value, unit, 'presets'))

        # Add the array description
        for desc in self.arrayInfo():
            ret.append(('desc_' + desc.name, desc.__dict__, '', '', 'general'))

        return ret


class ControlDetector(Detector):
    """
    This is a base class for classes which wish to coordinate multiple
    detectors. The model is that there are multiple slave detectors (like
    Histogram Memories) and one trigger detector which when started,
    actually starts data acquisition on the assembly. This implementation
    passes most Detector methods through to all participating detectors.
    start() and doIsCompleted() are implemented in such a way that it does
    the right thing for the SINQ combination of el737 counter box as
    trigger and HM slaves.
    """

    attached_devices = {'trigger':
                        Attach('Detector which triggers data acquisition',
                               Detector),
                        'slave_detectors': Attach('Slave detectors',
                                                  Measurable,
                                                  multiple=True,
                                                  optional=True),
                        }
    _slaves_stopped = False

    def doSetPreset(self, **preset):
        for det in self._attached_slave_detectors:
            det.setPreset(**preset)
        self._attached_trigger.setPreset(**preset)

    def doPrepare(self):
        for det in self._attached_slave_detectors:
            det.prepare()
        self._attached_trigger.prepare()

    def doStart(self):
        for det in self._attached_slave_detectors:
            det.start()
        self._attached_trigger.start()
        self._slaves_stopped = False

    def doIsCompleted(self):
        if self._attached_trigger.isCompleted():
            if not self._slaves_stopped:
                for det in self._attached_slave_detectors:
                    det.stop()
                    self._slaves_stopped = True
                    return False
            for det in self._attached_slave_detectors:
                if not det.isCompleted():
                    return False
            return True
        else:
            return False

    def doFinish(self):
        for det in self._attached_slave_detectors:
            det.finish()
        self._attached_trigger.finish()

    def readResults(self, quality):
        data, arrays = self._attached_trigger.readResults(quality)
        for det in self._attached_slave_detectors:
            d1, ar2 = det.readResults(quality)
            data = data + d1
            arrays = arrays + ar2
        return data, arrays

    def doPause(self):
        self._attached_trigger.pause()
        for det in self._attached_slave_detectors:
            det.pause()

    def doResume(self):
        for det in self._attached_slave_detectors:
            det.resume()
        self._attached_trigger.resume()

    def doStop(self):
        self._attached_trigger.stop()
        for det in self._attached_slave_detectors:
            det.stop()

    def duringMeasurementHook(self, elapsed):
        res = self._attached_trigger.duringMeasurementHook(elapsed)
        if res:
            return res
        for det in self._attached_slave_detectors:
            res = det.duringMeasurementHook(elapsed)
            if res:
                return res

    def doInfo(self):
        res = self._attached_trigger.doInfo()
        for det in self._attached_slave_detectors:
            res = res + det.doInfo()
        return res

    def presetInfo(self):
        return self._attached_trigger.presetInfo()

    def valueInfo(self):
        if not self._attached_trigger:
            self.doInit('')
        res = self._attached_trigger.valueInfo()
        for det in self._attached_slave_detectors:
            res = res + det.valueInfo()
        return res

    def arrayInfo(self):
        res = self._attached_trigger.arrayInfo()
        for det in self._attached_slave_detectors:
            res = res + det.arrayInfo()
        return res

    def doRead(self, maxage=0):
        res = self._attached_trigger.doRead(maxage)
        for det in self._attached_slave_detectors:
            res = res + det.doRead(maxage)
        return res

    def doReadArrays(self):
        res = self._attached_trigger.doReadArrays()
        for det in self._attached_slave_detectors:
            res = res + det.doReadArrays()
        return res
