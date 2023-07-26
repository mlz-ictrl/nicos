# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Measurable, Param, Value, pvname, status
from nicos.devices.generic import Detector
from nicos.devices.generic.detector import CounterChannelMixin, \
    TimerChannelMixin
from nicos.utils import uniq

from nicos_ess.devices.epics.detector import \
    EpicsActiveChannel as ESSEpicsActiveChannel
from nicos_sinq.devices.epics.scaler_record import EpicsScalerRecord


class EpicsActiveChannel(ESSEpicsActiveChannel):
    """
    SINQ EL737 counter boxes are getting old and overrun their
    presets rarely but frequently enough to be a problem. This code
    together with SinqDetector.doStatus() tries to detect the problem
    and stop the counter in such a case.
    """
    parameters = {
        'controlpv':
            Param('PV to check for overrun',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
    }

    def _get_pv_parameters(self):
        readable_params = ESSEpicsActiveChannel._get_pv_parameters(self)
        return readable_params | {'controlpv'}

    def presetReached(self, name, value, maxage):
        """Return true if the preset for *name* has overrun the given
        *value*.
        """
        if name in self._presetmap and value > 0:
            # Give it 10% grace in order to allow for normal counter box
            # operation
            return self._get_pv('controlpv') >= 1.1 * value
        return False


class EpicsTimerActiveChannel(TimerChannelMixin, EpicsActiveChannel):
    """
    Manages time presets
    """
    _presetmap = {'t', 'timer'}

    def valueInfo(self):
        return (Value('timepreset', unit='sec', fmtstr='%s'), )


class EpicsCounterActiveChannel(CounterChannelMixin, EpicsActiveChannel):
    """
    Manages monitor presets
    """
    _presetmap = {'m', 'monitor'}

    def valueInfo(self):
        return (Value('monitorpreset', unit='counts', fmtstr='%d'), )


class SinqDetector(EpicsScalerRecord):
    """Custom detector for SINQ.

    Only time and monitor presets are present.
    """

    attached_devices = {
        'timepreset': Attach('Device to set the preset time',
                             TimerChannelMixin),
        'monitorpreset': Attach('Device to set the monitor preset',
                                CounterChannelMixin)
    }

    parameters = {
        'check_overrun': Param('Flag to enable overrun checking',
                               type=bool, default=False, settable=False,
                               userparam=False),
    }

    monitor_preset_names = ['m', 'monitor']
    time_preset_names = ['t', 'time']

    def _presetiter(self):
        for name in self.monitor_preset_names:
            yield name, self._attached_monitorpreset, 'monitor'
        for name in self.time_preset_names:
            yield name, self._attached_timepreset, 'time'

    def _collectControllers(self):
        self._channels = uniq(self._channels + [self._attached_monitorpreset,
                                                self._attached_timepreset])
        EpicsScalerRecord._collectControllers(self)

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
            self.log.debug('Using the best preset')
            # The best preset is the one which is not 0,
            # The monitor preset is preferred
            monname = list(countpreset)[0]
            timename = list(timepreset)[0]
            monval = preset[monname]
            timeval = preset[timename]
            if monval > 0:
                for name in timepreset:
                    preset.pop(name)
                timepreset = set()
                timeval = 0
            elif timeval > 0:
                for name in countpreset:
                    preset.pop(name)
                countpreset = set()

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

        self._lastpreset = preset.copy()

        # Let the parent handle the rest
        EpicsScalerRecord.doSetPreset(self, **preset)

    def _getPreset(self, preset):
        if preset:
            return preset
        # None given, deduce from values
        result = {}
        timepreset = self._attached_timepreset.read()
        monpreset = self._attached_monitorpreset.read()
        if monpreset[0] > 0:
            # Prefer the monitor preset over the timepreset
            # This reflects SINQ usage
            # When we have a time preset, other logic ensures
            # that the monitor preset is 0
            result['m'] = monpreset[0]
            return result
        result['t'] = max(1, timepreset[0])
        return result

    def doInfo(self):
        ret = EpicsScalerRecord.doInfo(self)

        # Check for the mode and preset
        mode = ''
        value = 0
        unit = ''
        for d in self._controlchannels:
            for pkey in self._presetkeys.items():
                if pkey and pkey[1][0].name == d.name:
                    preselection = d.preselection
                    if preselection != 0:
                        value = preselection
                        unit = d.unit
                        mode = 'timer' if pkey[0].startswith('t') \
                            else 'monitor'
                        break
        ret.append(('mode', mode, mode, '', 'presets'))
        ret.append(('preset', value, '%s' % value, unit, 'presets'))

        # Add the array description
        for desc in self.arrayInfo():
            ret.append(('desc_' + desc.name, desc.__dict__, '', '', 'general'))

        return ret

    def doStatus(self, maxage=0):
        st, txt = EpicsScalerRecord.doStatus(self, maxage)
        if self.check_overrun and st == status.BUSY:
            for controller in self._controlchannels:
                for (name, value) in self._channel_presets.get(controller, ()):
                    if controller.presetReached(name, value, maxage):
                        self.log.warning('Stopping overrun counter!')
                        self.stop()
        return st, txt


class ControlDetector(Detector):
    """
    Base class for classes which wish to coordinate multiple detectors.

    The model is that there are multiple follower detectors (like
    Histogram Memories) and one trigger detector which when started,
    actually starts data acquisition on the assembly. This implementation
    passes most Detector methods through to all participating detectors.
    start() and doIsCompleted() are implemented in such a way that it does
    the right thing for the SINQ combination of el737 counter box as
    trigger and HM follower.
    """

    attached_devices = {
        'trigger': Attach('Detector which triggers data acquisition',
                          Detector),
        'followers': Attach('Follower detectors', Measurable,
                            multiple=True, optional=True),
    }
    _slaves_stopped = False
    _followers_stopped = False

    def doSetPreset(self, **preset):
        for det in self._attached_followers:
            det.setPreset(**preset)
        self._attached_trigger.setPreset(**preset)

    def _getPreset(self, preset):
        return self._attached_trigger._getPreset(preset)

    def doPrepare(self):
        for det in self._attached_followers:
            det.prepare()
        self._attached_trigger.prepare()

    def doStart(self):
        for det in self._attached_followers:
            det.start()
        self._attached_trigger.start()
        self._followers_stopped = False

    def doIsCompleted(self):
        if self._attached_trigger.isCompleted():
            if not self._followers_stopped:
                for det in self._attached_followers:
                    det.stop()
                self._followers_stopped = True
                return False
            for det in self._attached_followers:
                if not det.isCompleted():
                    return False
            return True
        else:
            return False

    def doFinish(self):
        for det in self._attached_followers:
            det.finish()
        self._attached_trigger.finish()

    def readResults(self, quality):
        data, arrays = self._attached_trigger.readResults(quality)
        for det in self._attached_followers:
            d1, ar2 = det.readResults(quality)
            data = data + d1
            arrays = arrays + ar2
        return data, arrays

    def doPause(self):
        self._attached_trigger.pause()
        for det in self._attached_followers:
            det.pause()

    def doResume(self):
        for det in self._attached_followers:
            det.resume()
        self._attached_trigger.resume()

    def doStop(self):
        self._attached_trigger.stop()
        for det in self._attached_followers:
            det.stop()

    def duringMeasureHook(self, elapsed):
        res = self._attached_trigger.duringMeasureHook(elapsed)
        if res:
            return res
        for det in self._attached_followers:
            res = det.duringMeasureHook(elapsed)
            if res:
                return res

    def doInfo(self):
        res = self._attached_trigger.doInfo()
        for det in self._attached_followers:
            res = res + det.doInfo()
        return res

    def presetInfo(self):
        return self._attached_trigger.presetInfo()

    def valueInfo(self):
        if not self._attached_trigger:
            self.doInit('')
        res = self._attached_trigger.valueInfo()
        for det in self._attached_followers:
            res = res + det.valueInfo()
        return res

    def arrayInfo(self):
        res = self._attached_trigger.arrayInfo()
        for det in self._attached_followers:
            res = res + det.arrayInfo()
        return res

    def doRead(self, maxage=0):
        res = self._attached_trigger.doRead(maxage)
        for det in self._attached_followers:
            res = res + det.doRead(maxage)
        return res

    def doReadArrays(self, quality):
        res = self._attached_trigger.doReadArrays(quality)
        for det in self._attached_followers:
            res += det.doReadArrays(quality)
        return res

    def doReset(self):
        self._attached_trigger.reset()
        for det in self._attached_slave_detectors:
            det.reset()
        return self.doStatus()

    def _collectControllers(self):
        self._channels = self._attached_trigger._channels
