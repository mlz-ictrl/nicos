# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************
"""
This module contains a devices for interfacing with the Sinq Epics DAQ Interface.

This replaces the following files:
    - nicos_sinq/devices/detector.py
    - nicos_sinq/devices/epics/detector.py
    - nicos_sinq/devices/epics/scaler_record.py
"""

import numpy as np

from nicos import session
from nicos.core import POLLER, SIMULATION, Attach, Moveable, Override, Param, \
    Readable, Value, floatrange, intrange, none_or, nonzero, oneof, pvname, \
    status
from nicos.core.constants import MASTER
from nicos.core.errors import UsageError
from nicos.core.mixins import CanDisable, HasLimits
from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics import EpicsDevice
from nicos.devices.generic.detector import ActiveChannel, \
    CounterChannelMixin, Detector, PassiveChannel, TimerChannelMixin


class DAQEpicsDevice(EpicsDevice):
    """
    Base device for configuring SINQ DAQ PVs.

    Inheriting Classes are expected to define a dictionary `_daqpvs`, the keys
    of which are aliases for PVs used for interacting with the DAQ System. When
    doing a Get or Put, the PV in the dictionary will be prefixed by
    `daqpvprefix`.
    """

    parameters = {
        'daqpvprefix':
            Param('Prefix for SINQ DAQ PV Interface',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=False,
                 ),
    }

    parameter_overrides = {
        'fmtstr': Override(userparam=False, settable=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False),
        'unit': Override(mandatory=False, userparam=False,
                         settable=False, volatile=True),
        'monitor': Override(default=True), # Enable Callbacks by default
    }

    def _get_pv_parameters(self):
        return self._daqpvs.keys()

    def _get_pv_name(self, pvparam):
        if pvparam in self._daqpvs.keys():
            return ':'.join([self.daqpvprefix, self._daqpvs[pvparam]])
        return EpicsDevice._get_pv_name(self, pvparam)

    # TODO I am not sure if this is something I broke? or in general broken
    # in the version of caproto we have?
    # So I am temporarily overriding to fix this here
    def _get_pv(self, pvparam, as_string=False):
        value = EpicsDevice._get_pv(self, pvparam, as_string)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, np.integer):
            return int(value)
        return value

    # TODO I am overriding this due to the same problem
    def value_change_callback(self, name, param, value, units, severity,
                              message, **kwargs):
        cache_key = self._get_cache_relation(param)
        if cache_key and self._cache:
            if isinstance(value, np.floating):
                self._setROParam(cache_key, float(value))
            elif isinstance(value, np.integer):
                self._setROParam(cache_key, int(value))
            else:
                self._setROParam(cache_key, value)
            if param == 'readpv':
                self._setROParam('unit', units)

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doReadUnit(self):
        return self._epics_wrapper.get_units(self._param_to_pv['readpv'])


class DAQChannelEpicsDevice(DAQEpicsDevice):
    """
    Base device for configuring SINQ DAQ PVs that are channel specific.

    This is a specialised variant of the `DAQEpicsDevice`, that expects the
    items in the `_daqpvs` dictionary, to also contain a field `{CHANNEL}`,
    which will be replaced with the configured `channel` parameter of this
    device. This enables channel specific PVs to be interacted with.
    """

    parameters = {
        'channel':
            Param('Physical Input Channel',
                  type=int,
                  mandatory=True,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=True,
                  internal=False,
                 ),
    }

    def _get_pv_name(self, pvparam):
        if pvparam in self._daqpvs.keys():
            return ':'.join([
                self.daqpvprefix,
                self._daqpvs[pvparam].format(channel=self.channel)
            ])
        return EpicsDevice._get_pv_name(self, pvparam)


class DAQChannel(DAQChannelEpicsDevice, CounterChannelMixin, PassiveChannel):
    """
    Retrieves the Count and Rate from the configured `channel` of the
    configured SINQ DAQ System.
    """

    parameters = {
        'preparing':
            Param('Internal: set when the channel should be cleared',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                 ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'presetaliases': Override(mandatory=False, internal=False,
                                  settable=True, userparam=True),
    }

    valuetype = int

    _daqpvs = {
        'readpv': 'M{channel}',
        'ratepv': 'R{channel}',
        'resetpv': 'C{channel}',
        'statuspv': 'S{channel}',
    }

    def doPrepare(self):
        self.preparing = True
        # Force the status change to occur before resetting
        self.status(0)
        self._put_pv('resetpv', 1, timeout=self.epicstimeout)

    def _get_status_parameters(self):
        return {'ratepv', 'statuspv'}

    def status_change_callback(self, name, param, value, units, severity,
                               message, **kwargs):
        if not value:
            self._setROParam('preparing', False)
        self._setROParam('status', self.doStatus())

    def doStatus(self, maxage=0):
        try:
            if self._get_pv('statuspv') or self.preparing:
                return status.BUSY, ''

            rate = self._get_pv('ratepv')
            rate_units = self._epics_wrapper.get_units(self._param_to_pv['ratepv'])
            return status.OK, f'Rate: {rate:.2f} {rate_units}'

        except TimeoutError:
            return status.ERROR, 'timeout reading rate'

    def doReset(self):
        self.preparing = False


class DAQTime(DAQEpicsDevice, TimerChannelMixin, PassiveChannel):
    """
    Retrieves the elapsed time from the configured `channel` of the
    configured SINQ DAQ System.
    """

    parameters = {
        'preparing':
            Param('Internal: set when a device should be cleared',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                 ),
    }

    parameter_overrides = {
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'fmtstr': Override(default='%.3f'),
        'description': Override(mandatory=False, internal=True, prefercache=False,
                                default=('The Elapsed Time measured during the '
                                         'current/most recent count')),
        'presetaliases': Override(mandatory=False, internal=False,
                                  settable=True, userparam=True),
    }

    _daqpvs = {
        'readpv': 'ELAPSED-TIME',
        'resetpv': 'CT',
        'statuspv': 'ETS',
    }

    valuetype = float

    def doPrepare(self):
        self.preparing = True
        # Force the status change to occur before resetting
        self.status(0)
        self._put_pv('resetpv', 1, timeout=self.epicstimeout)

    def _get_status_parameters(self):
        return {'statuspv'}

    def status_change_callback(self, name, param, value, units, severity,
                               message, **kwargs):
        if not value:
            self._setROParam('preparing', False)
        self._setROParam('status', self.doStatus())

    def doStatus(self, maxage=0):
        try:
            if self._get_pv('statuspv') or self.preparing:
                return status.BUSY, ''
            return status.OK, ''

        except TimeoutError:
            return status.ERROR, 'timeout reading elapsed time'

    def doReset(self):
        self.preparing = False


class DAQPreset(DAQEpicsDevice, ActiveChannel):
    """
    An active detector channel, that configures and starts counts based on
    in-hardware time- or count-based presets measured within the SINQ DAQ
    system.

    Both a time and count preset can be set simultaneously, but in this case,
    only the time-based preset is checked by the hardware. The count-based
    preset, in such a case, will instead be checked by Nicos, meaning that the
    value may overshoot the desired count.

    Channels that can be selected for an in-hardware count-based preset should
    be attached by adding them to the `channels` list in the device setup file.
    This, however, doesn't guarantee they can be selected. Some SINQ DAQ
    systems support only specific channels, so the list will be filtered via
    the limits provided by Epics and may in the end show only one channel.
    """

    parameters = {
        'started_count':
            Param('Internal: set when a count was started via Nicos',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                 ),
        'hardware_time':
            Param('Internal: in-hardware time preset',
                  type=none_or(nonzero(floatrange(0, float('inf')))),
                  default=1,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='sec',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                 ),
        'hardware_count':
            Param('Internal: in-hardware count preset',
                  type=none_or(nonzero(intrange(0, 2147483647))),
                  default=1000,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='cts',
                  fmtstr='%d',
                  userparam=False,
                  internal=True,
                 ),
        'monitor_channel':
            Param('currently configured channel for count-based preset',
                  type=str,
                  mandatory=False,
                  settable=True,
                  volatile=True,
                  unit='',
                  fmtstr='%s',
                  userparam=True,
                  internal=True,
                 ),
        'used_preset':
            Param(('Internal: Set when the next call to `setChannelPreset` '
                   'should first clear all presets'),
                  type=bool,
                  default=True,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  prefercache=False,
                  userparam=True,
                  internal=True,
                 ),
    }

    parameter_overrides = {
        'presetaliases': Override(default=('t', 'm'), mandatory=False,
                                  internal=True, settable=False,
                                  userparam=True, prefercache=False),
        'fmtstr': Override(settable=True, internal=True),
        'unit': Override(volatile=False, settable=True,
                         mandatory=False, internal=True),
        'preselection': Override(volatile=False, settable=False,
                                 userparam=False, internal=True)
    }

    # Channels that can be selected for a hardware based preset are limited to
    # those specified in this list. We also make use of the list in order to
    # allow the user to select the name of the device associate with the
    # channel, instead of just a number.
    attached_devices = {
        'channels':
            Attach('Channels that can be selected for in-hardware count presets',
                   DAQChannel,
                   multiple=True,
                   optional=False
                  ),
        'time_channel':
            Attach('Time channels that can be selected for in-hardware time presets',
                   DAQTime,
                   multiple=False,
                   optional=False
                  ),
    }

    _daqpvs = {
        'statuspv': 'STATUS',
        'presetcountpv': 'PRESET-COUNT',
        'presettimepv': 'PRESET-TIME',
        'totalchannelspv': 'CHANNELS',
        'resetpv': 'FULL-RESET',
        'pausepv': 'PAUSE',
        'continuepv': 'CONTINUE',
        'stoppv': 'STOP',
        'errormsgpv': 'MsgTxt',
        'monitorchannelpv': 'MONITOR-CHANNEL',
        'monitorchannelrbvpv': 'MONITOR-CHANNEL_RBV',
    }

    _cache_relations = {'monitorchannelrbvpv': 'value'}

    _channel_callback = None

    def doPreinit(self, mode):
        DAQEpicsDevice.doPreinit(self, mode)

        if mode == SIMULATION:
            self._mapping = {
                channel.name: channel
                for channel in self._attached_channels
            }

        else:
            absmin, absmax = self._get_limits('monitorchannelpv')

            self._mapping = {
                channel.name: channel
                for channel in self._attached_channels
                # If you set absmin == absmax in epics, regardless of their
                # values here you will just end up with absmin == absmax == 0,
                # so we can't know here from the limits that it should be
                # channel 1.
                if (absmin == absmax and channel.channel == 1)
                or (channel.channel >= absmin and channel.channel <= absmax)
            }

        self._inv_mapping = {
            channel.channel: channel
            for _, channel in self._mapping.items()
        }

        self.parameters['monitor_channel'].type = oneof(*self._mapping)

        # In simulation mode and when running tests, each parameter value is
        # set to the default of the parameter. So we ensure there is a default
        # set.
        self.parameters['monitor_channel'].default = list(self._mapping)[0]

    def doInit(self, mode):
        DAQEpicsDevice.doInit(self, mode)

        if mode == MASTER:
            self.used_preset = True

    def presetInfo(self):
        if self._presetmap is not None:
            return set(self._presetmap)
        self._presetmap = {
            alias: 0
            for alias in self.presetaliases
        }
        return set(self._presetmap)

    @property
    def isTimePreset(self):
        """If in-hardware preset is time based."""
        return self.hardware_time or not self.hardware_count

    def doRead(self, maxage=0):
        if self.isTimePreset:
            return self._attached_time_channel.read()
        return self._mapping[self.monitor_channel].read()

    def value_change_callback(self, name, param, value, units, severity,
                              message, **kwargs):
        self._setROParam('value', self.doRead())

    def doReadMonitor_Channel(self):
        channel = self._get_pv('monitorchannelrbvpv')
        if channel == 0:
            return "None"
        return self._inv_mapping[channel].name

    def doWriteMonitor_Channel(self, newValue):
        return self._put_pv('monitorchannelpv', self._mapping[newValue].channel, timeout=self.epicstimeout)

    def valueInfo(self):
        if self.isTimePreset:
            return (Value(self._attached_time_channel.name, unit=self.unit, fmtstr='%.3f'), )
        return (Value(self.monitor_channel, unit=self.unit, fmtstr='%d'), )

    def doReadUnit(self):
        if self.isTimePreset:
            return 'sec'
        return 'cts'

    def _update_value_callback(self, channel):
        if session.sessiontype != POLLER:

            if self._channel_callback:
                self._epics_wrapper.close_subscription(self._channel_callback)
                self._channel_callback = None

            pvname = channel._get_pv_name('readpv')
            self._channel_callback = channel._subscribe(
                    self.value_change_callback, pvname, 'readpv')

    def doStart(self):
        if not (self.hardware_time or self.hardware_count):
            raise UsageError(("Either a 't' or 'm' preset must be specified "
                              "to use this detector hardware."))

        self.used_preset = True
        self.started_count = True

        if self.hardware_time and self.hardware_count:
            self.log.warning((
                'Both Time and Count presets specified. '
                'Time will be checked in-hardware, Count via Nicos.'))

        self.status(0)

        if self.hardware_time:
            self._update_value_callback(self._attached_time_channel)
            self._put_pv('presettimepv', self.hardware_time, timeout=self.epicstimeout)
        else:
            self._update_value_callback(self._mapping[self.monitor_channel])
            self._put_pv('presetcountpv', self.hardware_count, timeout=self.epicstimeout)

    def setChannelPreset(self, name, value):
        PassiveChannel.setChannelPreset(self, name, value)

        if self.used_preset:
            self.hardware_time = None
            self.hardware_count = None
            self.used_preset = False

        if name == 't':
            self.hardware_time = value

        if name == 'm':
            self.hardware_count = value

        self.unit = 'sec' if self.isTimePreset else 'cts'
        self.fmtstr = '%.3f' if self.isTimePreset else '%d'

    def doStop(self):
        self.started_count = False
        self._put_pv('stoppv', 1)

    def doFinish(self):
        self.started_count = False
        self._put_pv('stoppv', 1)

    def doPause(self):
        self._put_pv('pausepv', 1)
        return True

    def doResume(self):
        self._put_pv('continuepv', 1)

    def _get_status_parameters(self):
        return {'statuspv', 'monitorchannelrbvpv'}

    def status_change_callback(self, name, param, value, units, severity,
                               message, **kwargs):
        self._setROParam('status', self.doStatus())

    def doStatus(self, maxage=0):
        try:
            st_code = self._get_pv('statuspv')

            started_count = self.started_count
            if st_code != 0 and started_count:
                self._setROParam('started_count', False)
                started_count = False

            time_channel = self._attached_time_channel
            count_channel = self._mapping[self.monitor_channel]

            if self.isTimePreset:
                status_msg = '%.3f sec on %s' % (self.hardware_time, time_channel.name)
            else:
                status_msg = "%d cts on %s" % (self.hardware_count, count_channel.name)

            if st_code == 1 or started_count:

                if self.hardware_time is not None and time_channel.presetReached(time_channel.name, self.hardware_time, maxage):
                    return status.OK, 'Preset: ' + status_msg

                if self.hardware_count is not None and count_channel.presetReached(count_channel.name, self.hardware_count, maxage):
                    return status.OK, 'Preset: ' + status_msg

                return status.BUSY, 'Counting: ' + status_msg

            elif st_code == 0:
                # On the Epics side, we guarantee that the channels update to their
                # final values before switching the status from `Counting` back to
                # `Idle`. We, however, have no guarantee of the order that the callbacks
                # are processed by Nicos. So we force all channels to be read before
                # changing the status on the Nicos side back to Idle after a count.
                time_channel.read(0)

                for channel in self._attached_channels:
                    channel.read(0)

                return status.OK, 'Preset: ' + status_msg

            elif st_code == 2:
                return status.BUSY, 'Low Rate' # TODO might be better to use WARN, but that stops the count

            elif st_code == 3:
                return status.BUSY, 'Paused'

            else:
                return status.ERROR, 'DAQ Error: %s' % self._get_pv('errormsgpv')

        except TimeoutError:
            return status.ERROR, 'timeout getting DAQ Hardware status'

    def doReset(self):
        self.started_count = False
        self.used_preset = True

    def full_reset(self):
        # This doesn't just clear the channels, it resets the box completely
        # back to default settings.
        self._put_pv('resetpv', 1, timeout=self.epicstimeout)


class DAQMinThresholdChannel(CanDisable, DAQEpicsDevice, MappedMoveable):
    """
    Configures which channel should be monitored in-hardware to detect whether
    or not sufficient Neutron's are flowing for a measurement.
    """

    parameters = {
        'threshold_monitor':
            Param('Chosen Channel for Low Rate Detection',
                  type=int,
                  default=1,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='CH',
                  fmtstr='%d',
                  userparam=True,
                  internal=True,
                 ),
        'device_threshold_monitor':
            Param('In-Hardware Configured Channel for Low Rate Detection',
                  type=int,
                  mandatory=False,
                  settable=True,
                  volatile=True,
                  unit='CH',
                  fmtstr='%d',
                  userparam=False,
                  internal=True,
                 ),
    }

    parameter_overrides = {
        'fmtstr': Override(userparam=False, default='%s'),
        'target': Override(volatile=True),
        'mapping': Override(mandatory=False, internal=True, userparam=False),
        'description': Override(mandatory=False, internal=True, prefercache=False,
                                default='Monitored Low Rate Channel'),
    }

    # Channels that can be monitored for low beam rate are limited to those
    # specified in this list.
    attached_devices = {
        'channels':
            Attach('Channels that can be selected for in-hardware count presets',
                   DAQChannel,
                   multiple=True,
                   optional=False
                  ),
    }

    _daqpvs = {
        'writepv': 'THRESHOLD-MONITOR',
        'readpv': 'THRESHOLD-MONITOR_RBV',
    }

    _cache_relations = {
        'readpv': 'value'
    }

    valuetype = str

    def doPreinit(self, mode):
        DAQEpicsDevice.doPreinit(self, mode)

        absmin, absmax = 0, 2**32

        if mode != SIMULATION:
            absmin, absmax = self._get_limits('writepv')

        mapping = {
            channel.name: channel.channel
            for channel in sorted(self._attached_channels, key=lambda x: x.channel)
            if channel.channel >= absmin and channel.channel <= absmax
        }

        self._setROParam('mapping', mapping)

        # We need to do this here, as `target` requires the mapping to be initialised
        self._inverse_mapping = {}
        for k, v in mapping.items():
            self._inverse_mapping[v] = k

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)

        if mode == MASTER:
            self.doReset()

    def doReset(self):
        # make sure the target is equal to the current value
        hardware_value = self._get_pv('readpv')
        self._setROParam('threshold_monitor',
                         hardware_value if hardware_value else 1)

    def doReadUnit(self):
        return ''

    def doReadDevice_Threshold_Monitor(self):
        return self._get_pv('readpv')

    def doWriteDevice_Threshold_Monitor(self, newValue):
        return self._put_pv('writepv', newValue)

    def doWriteThreshold_Monitor(self, newValue):
        if self.isEnabled():
            self.device_threshold_monitor = newValue

    def doStart(self, target):
        self.threshold_monitor = self._mapTargetValue(target)
        self.status()

    def doReadTarget(self):
        return self._mapReadValue(self.threshold_monitor)

    def doRead(self, maxage=0):
        if self.isEnabled():
            return self._mapReadValue(self.device_threshold_monitor)
        return self._mapReadValue(self.threshold_monitor)

    def doStatus(self, maxage=0):
        try:
            if self.isEnabled():
                if self.target != self.read():
                    return status.BUSY, ''
                return status.OK, ''
            return status.DISABLED, ''
        except TimeoutError:
            return status.ERROR, 'timeout reading configured channel'

    def _get_status_parameters(self):
        # Otherwise takes a while to update
        return {'writepv'}

    def doEnable(self, on):
        if on:
            self.device_threshold_monitor = self.threshold_monitor

        else:
            self.device_threshold_monitor = 0

    def isEnabled(self):
        return self.device_threshold_monitor > 0


class DAQMinThreshold(DAQEpicsDevice, HasLimits, Moveable):
    """
    The threshold value used to determine if enough Neutrons are flowing for a
    count to start/continue.
    """

    parameters = {
        'threshold':
            Param('Low Rate Threshold',
                  type=float,
                  default=0.,
                  mandatory=False,
                  settable=True,
                  volatile=True,
                  fmtstr='%.3f',
                  userparam=True,
                  internal=True,
                 ),
    }

    parameter_overrides = {
        'fmtstr': Override(userparam=False, default='%d'),
        'target': Override(volatile=True),
        'abslimits': Override(mandatory=False, volatile=True),
        'description': Override(mandatory=False, internal=True, prefercache=False,
                                default='Low Rate Threshold'),
    }

    attached_devices = {
        'min_rate_channel':
            Attach('Device for configuring threshold channel',
                   DAQMinThresholdChannel,
                   multiple=False,
                   optional=False
                  ),
    }

    _daqpvs = {
        'readpv': 'THRESHOLD_RBV',
        'writepv': 'THRESHOLD',
        # Just to trigger enable disable callback
        'thresholdmonitorrbvpv': 'THRESHOLD-MONITOR_RBV',
    }

    _cache_relations = {
        'readpv': 'value'
    }

    def doPreinit(self, mode):
        DAQEpicsDevice.doPreinit(self, mode)

        if mode == SIMULATION:
            self.valuetype = nonzero(intrange(0, 2147483647))
        else:
            absmin, absmax = self._get_limits('writepv')
            self.valuetype = intrange(absmin, absmax)

    def doInit(self, mode):
        if mode == MASTER:
            self.doReset()

    def doReset(self):
        # make sure the target is equal to the current value
        self._put_pv('writepv', self._get_pv('readpv'))

    def doReadThreshold(self):
        return self._get_pv('readpv')

    def doWriteThreshold(self, newValue):
        return self._put_pv('writepv', newValue)

    def doStart(self, target):
        self.threshold = target

    def doReadTarget(self):
        return self._get_pv('writepv')

    def doRead(self, maxage=0):
        if self._attached_min_rate_channel.isEnabled():
            return self.threshold
        return 0.

    def doStatus(self, maxage=0):
        try:
            if self._attached_min_rate_channel.isEnabled():
                channel_status, _ = self._attached_min_rate_channel.status()
                if channel_status == status.BUSY or self.target != self.read():
                    return status.BUSY, ''
                return status.OK, ''
            else:
                return status.DISABLED, ''
        except TimeoutError:
            return status.ERROR, 'timeout reading configured threshold'

    def _get_status_parameters(self):
        # Otherwise takes a while to update
        return {'thresholdmonitorrbvpv', 'writepv'}

    def doReadAbslimits(self):
        return self._get_limits('writepv')


class DAQGate(DAQChannelEpicsDevice, Moveable):
    """
    Provides the ability to configure hardware gating channels.

    If enabled, a count will only start if the specified channel is
    held high/low.
    """

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'target': Override(volatile=True),
        'unit': Override(default='', mandatory=False, internal=True, userparam=False),
    }

    _cache_relations = {
        'readpv': 'value'
    }

    _daqpvs = {
        'readpv': 'GATE-{channel}_RBV',
        'writepv': 'GATE-{channel}',
    }

    # We could also read this values from Epics
    valuetype = oneof('Disabled', 'Trigger High', 'Trigger Low')

    def doInit(self, mode):
        if mode == MASTER:
            self.doReset()

        DAQChannelEpicsDevice.doInit(self, mode)

    def doReset(self):
        # make sure the target is equal to the current value
        self._put_pv('writepv', self._get_pv('readpv', as_string=True), timeout=self.epicstimeout)

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)

    def doReadTarget(self):
        return self._get_pv('writepv', as_string=True)

    def doStart(self, target):
        if target != self.read():
            self._put_pv('writepv', target)
        self.status(0)

    def doStatus(self, maxage=0):
        try:
            if self.read() != self.target:
                return status.BUSY, ''
            return status.OK, ''
        except TimeoutError:
            return status.ERROR, 'timeout reading configured gate settings'

    def _get_status_parameters(self):
        # Otherwise takes a while to update
        return {'writepv'}

    def _subscribe(self, change_callback, pvname, pvparam):
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback,
                                             as_string=True)


class DAQTestGen(CanDisable, DAQEpicsDevice, Readable):
    """
    Configures the Signal Test Generator built into some DAQ Systems. This is
    only for testing by us, and not typically meant to be configured on
    instruments.
    """

    parameters = {
        'lowrate':
            Param('Multiple of 10ns that the signal is low',
                  type=int,
                  userparam=True,
                  settable=True,
                  volatile=True,
                  mandatory=False,
                  internal=True
                 ),
        'highrate':
            Param('Multiple of 10ns that the signal is high',
                  type=int,
                  userparam=True,
                  settable=True,
                  volatile=True,
                  mandatory=False,
                  internal=True
                 ),
        # There is no way to readback from the box whether or not this is enabled
        'enabled':
            Param('Whether the test generator is enabled',
                  type=oneof('OFF', 'ON'),
                  default='ON',
                  userparam=True,
                  settable=True,
                  volatile=True,
                  mandatory=False,
                  internal=True
                 ),
    }

    parameter_overrides = {
        'fmtstr': Override(userparam=False, default='%s'),
        'unit': Override(volatile=False, mandatory=False),
        'description': Override(
            mandatory=False,
            internal=True,
            prefercache=False,
            default='Configuration for the channel 1 test signal generator'
        ),
    }

    _daqpvs = {
        'enabledpv': 'TESTGEN',
        'lowratepv': 'TESTGEN-LOWRATE',
        'highratepv': 'TESTGEN-HIGHRATE',
    }

    # No read pv
    _cache_relations = {}

    def doReadUnit(self):
        return ''

    valuetype = str

    def doReadHighrate(self):
        return self._get_pv('highratepv')

    def doWriteHighrate(self, newValue):
        return self._put_pv('highratepv', newValue)

    def doReadLowrate(self):
        return self._get_pv('lowratepv')

    def doWriteLowrate(self, newValue):
        return self._put_pv('lowratepv', newValue)

    def doRead(self, maxage=0):
        return f'{self.lowrate * 10}ns low / {self.highrate * 10}ns high'

    def doStatus(self, maxage=0):
        if self.enabled == 'ON':
            return status.OK, ''
        else:
            return status.DISABLED, ''

    def doEnable(self, on):
        if on:
            self.enabled = 'ON'
        else:
            self.enabled = 'OFF'

    def doReadEnabled(self):
        return self._get_pv('enabledpv', as_string=True)

    def doWriteEnabled(self, newValue):
        return self._put_pv('enabledpv', newValue)

    def _get_status_parameters(self):
        return {'enabledpv'}


class SinqDetector(Detector):
    """
    Identical to the default Detector class in core except for a small change
    in the preset generation.
    """

    def _presetiter(self):
        """Yield (name, device, type) tuples for all 'preset-able' devices."""
        for dev in self._attached_timers:
            # Removes this default, that is taken over by the hardware preset
            # if i == 0:
            #     yield ('t', dev, 'time')
            for preset in dev.presetInfo():
                yield (preset, dev, 'time')
        for dev in self._attached_monitors:
            for preset in dev.presetInfo():
                yield (preset, dev, 'monitor')
        for dev in self._attached_counters:
            # Removes this default, that is taken over by the hardware preset
            # For historical reasons, at Sinq we use 'm' instead of 'n'
            # if i == 0:
            #     yield ('n', dev, 'counts')
            for preset in dev.presetInfo():
                yield (preset, dev, 'counts')
        for dev in self._attached_images + self._attached_others:
            for preset in dev.presetInfo():
                yield (preset, dev, 'counts')
        yield ('live', None, 'other')
