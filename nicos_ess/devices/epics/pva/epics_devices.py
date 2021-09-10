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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""
This module contains some classes for NICOS - EPICS integration using p4p.
"""
import time

from nicos import session
from nicos.core import POLLER, SIMULATION, ConfigurationError, \
    DeviceMixinBase, HasLimits, Moveable, Override, Param, Readable, anytype, \
    floatrange, none_or, pvname, status
from nicos.devices.abstract import MappedMoveable
from nicos.utils import HardwareStub

from nicos_ess.devices.epics.pva.p4p import P4pWrapper

__all__ = [
    'EpicsDevice', 'EpicsReadable', 'EpicsStringReadable',
    'EpicsMoveable', 'EpicsAnalogMoveable', 'EpicsDigitalMoveable',
]


class EpicsDevice(DeviceMixinBase):
    hardware_access = True
    valuetype = anytype
    pv_status_parameters = set()
    _epics_subscriptions = set()
    _cache_relations = {'readpv': 'value'}

    parameters = {
        'epicstimeout': Param('Timeout for getting EPICS PVs',
                              type=none_or(floatrange(0.1, 60)),
                              userparam=False, mandatory=False, default=1.0),
        'monitor': Param('Use a PV monitor', type=bool, default=False),
    }

    # This will store PV objects for each PV param.
    _param_to_pv = {}
    _epics_wrapper = None
    _record_fields = {}
    _pvs = {}

    def doPreinit(self, mode):
        self._param_to_pv = {}
        self._pvs = {}

        self._epics_wrapper = P4pWrapper(self.epicstimeout)

        if mode != SIMULATION:
            for pvparam in self._get_pv_parameters():
                # Retrieve the actual PV name
                pvname = self._get_pv_name(pvparam)
                if not pvname:
                    raise ConfigurationError(self, 'PV for parameter %s was '
                                                   'not found!' % pvparam)
                # Check pv exists - throws if cannot connect
                self._epics_wrapper.connect_pv(pvname)
                self._param_to_pv[pvparam] = pvname
        else:
            for pvparam in self._get_pv_parameters():
                self._param_to_pv[pvparam] = HardwareStub(self)

    def doInit(self, mode):
        if mode != SIMULATION and self.monitor:
            self._register_pv_callbacks()

    def _register_pv_callbacks(self):
        self._epics_subscriptions = set()

        value_pvs = self._get_pv_parameters()
        status_pvs = self._get_status_parameters()
        if session.sessiontype == POLLER:
            self._subscribe_params(value_pvs, self.value_change_callback)
        else:
            self._subscribe_params(status_pvs or value_pvs,
                                   self.status_change_callback)

    def _subscribe_params(self, pvparams, change_callback):
        for pvparam in pvparams:
            pvname = self._get_pv_name(pvparam)
            subscription = self._subscribe(change_callback, pvname, pvparam)
            self._epics_subscriptions.add(subscription)

    def _subscribe(self, change_callback, pvname, pvparam):
        """
        Override this for custom behaviour in sub-classes.
        """
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback)

    def value_change_callback(self, name, param, value, severity, message,
                              **kwargs):
        """
        Override this for custom behaviour in sub-classes.
        """
        cache_key = self._get_cache_relation(param) or name
        self._cache.put(self._name, cache_key, value, time.time())

    def status_change_callback(self, name, param, value, severity, message,
                               **kwargs):
        """
        Override this for custom behaviour in sub-classes.
        """
        current_status = self.doStatus()
        self._cache.put(self._name, 'status', current_status, time.time())

    def connection_change_callback(self, name, pvparam, is_connected, **kwargs):
        if is_connected:
            self.log.debug('%s connected!', name)
        else:
            self.log.warn('%s disconnected!', name)

    def _get_cache_relation(self, param):
        # Returns the cache key associated with the parameter.
        return self._cache_relations.get(param, None)

    def _get_status_parameters(self):
        # Returns the parameters which indicate "movement" is happening.
        return self.pv_status_parameters

    def doShutdown(self):
        for sub in self._epics_subscriptions:
            self._epics_wrapper.close_subscription(sub)

    def _get_pv_parameters(self):
        return set(self._record_fields.keys())

    def _get_pv_name(self, pvparam):
        if hasattr(self, pvparam):
            return getattr(self, pvparam)
        stem = getattr(self, 'readpv')
        return '.'.join([stem, self._record_fields.get(pvparam, '')])

    def doStatus(self, maxage=0):
        # For most devices we only care about the status of the read PV
        pvname = self._get_pv_name('readpv')
        try:
            severity, msg = self._epics_wrapper.get_alarm_status(pvname)
        except TimeoutError:
            return status.ERROR, 'timeout reading status'
        if severity in [status.ERROR, status.WARN]:
            return severity, msg
        return status.OK, msg

    def _setMode(self, mode):
        # remove the PVs on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            for key in self._param_to_pv:
                self._param_to_pv[key] = HardwareStub(self)

    def _get_limits(self, pvparam):
        return self._epics_wrapper.get_limits(self._get_pv_name(pvparam))

    def _get_pv(self, pvparam, as_string=False):
        return self._epics_wrapper.get_pv_value(self._param_to_pv[pvparam],
                                                as_string=as_string)

    def _put_pv(self, pvparam, value, wait=False):
        self._epics_wrapper.put_pv_value(self._param_to_pv[pvparam], value,
                                         wait=wait)

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1, timeout=60):
        self._epics_wrapper.put_pv_value_blocking(self._param_to_pv[pvparam],
                                                  value, update_rate, timeout)


class EpicsReadable(EpicsDevice, Readable):
    """
    Handles EPICS devices that can only read a value.
    """
    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, userparam=False),
        'has_unit': Param('There is a EGU field', type=bool, default=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=False, volatile=True),
    }

    _record_fields = {
        'readpv': '',
        'units': 'EGU',
    }

    _cache_relations = {
        'readpv': 'value',
        'units': 'unit',
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        self.valuetype = self._epics_wrapper.get_pv_type(self._param_to_pv['readpv'])
        EpicsDevice.doInit(self, mode)

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def _get_pv_parameters(self):
        fields = set(self._record_fields.keys())
        if not self.has_unit:
            fields.remove('units')
        return fields

    def doReadUnit(self):
        if not self.has_unit:
            return ''
        return self._epics_wrapper.get_units(self._param_to_pv['readpv'])


class EpicsStringReadable(EpicsReadable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

    _record_fields = {
        'readpv': '',
    }

    _cache_relations = {
        'readpv': 'value',
    }

    def _get_pv_parameters(self):
        return {'readpv'}

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsMoveable(EpicsDevice, Moveable):
    """
    Handles EPICS devices which can set and read a value.
    """
    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, userparam=False),
        'writepv': Param('PV for writing device target',
                         type=pvname, mandatory=True, userparam=False),
        'targetpv': Param('Optional target readback PV.',
                          type=none_or(pvname), mandatory=False,
                          userparam=False)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=False, volatile=False),
        'target': Override(volatile=True),
    }

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target',
    }

    def _get_pv_parameters(self):
        if self.targetpv:
            return {'readpv', 'writepv', 'targetpv'}
        return {'readpv', 'writepv'}

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        EpicsDevice.doInit(self, mode)

        in_type = self._epics_wrapper.get_pv_type(self._param_to_pv['readpv'])
        out_type = self._epics_wrapper.get_pv_type(self._param_to_pv['writepv'])
        if in_type != self.valuetype:
            raise ConfigurationError(self, 'Input PV %r does not have the '
                                           'correct data type' % self.readpv)
        if out_type != self.valuetype:
            raise ConfigurationError(self, 'Output PV %r does not have the '
                                           'correct data type' % self.writepv)
        if self.targetpv:
            target_type = self._epics_wrapper.get_pv_type(
                self._param_to_pv['targetpv'])
            if target_type != self.valuetype:
                raise ConfigurationError(
                    self, 'Target PV %r does not have the '
                          'correct data type' % self.targetpv)

    def doReadTarget(self):
        if self.targetpv:
            return self._get_pv('targetpv')
        else:
            return self._get_pv('writepv')

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        self._put_pv('writepv', value)

    def doStop(self):
        self.doStart(self.doRead())


class EpicsStringMoveable(EpicsMoveable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target',
    }

    def _get_pv_parameters(self):
        return {'readpv', 'writepv'}

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsAnalogMoveable(HasLimits, EpicsMoveable):
    """
    Handles EPICS devices which can set and read a floating value.
    """
    valuetype = float

    parameters = {
        'has_unit': Param('There is a EGU field', type=bool, default=True),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
        'unit': Override(mandatory=False, settable=False, volatile=True),
    }

    _record_fields = {
        'readpv': '',
        'writepv': '',
        'units': 'EGU',
    }

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target',
        'units': 'unit',
    }

    def _get_pv_parameters(self):
        fields = set(self._record_fields.keys())
        if not self.has_unit:
            fields.remove('units')

        if self.targetpv:
            return fields | {'targetpv'}

        return fields

    def doReadUnit(self):
        if not self.has_unit:
            return ''
        return self._epics_wrapper.get_units(self._param_to_pv['readpv'])


class EpicsDigitalMoveable(EpicsAnalogMoveable):
    """
    Handles EPICS devices which can set and read an integer value.
    """
    valuetype = int

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }


class EpicsMappedMoveable(MappedMoveable, EpicsMoveable):
    valuetype = str

    parameters = {
        'ignore_stop': Param('Whether to do anything when stop is called',
                             type=bool, default=False, userparam=False),
    }

    parameter_overrides = {
        # MBBI, BI, etc. do not have units
        'unit': Override(mandatory=False, settable=False, volatile=False),
        # Mapping values are read from EPICS
        'mapping': Override(mandatory=False, settable=True, userparam=False)
    }

    def _get_pv_parameters(self):
        return {'readpv', 'writepv'}

    def _subscribe(self, change_callback, pvname, pvparam):
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback,
                                             as_string=True)

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        EpicsDevice.doInit(self, mode)
        MappedMoveable.doInit(self, mode)

        if session.sessiontype != POLLER:
            choices = self._epics_wrapper.get_value_choices(
                self._get_pv_name('readpv'))
            # Existing mapping is fixed, so must create and replace
            new_mapping = {}
            for i, choice in enumerate(choices):
                new_mapping[choice] = i
            self.mapping = new_mapping

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)

    def doStart(self, value):
        self._put_pv('writepv', value)

    def doStop(self):
        # Some devices will react on being re-sent the current position which
        # may not be appropriate
        if not self.ignore_stop:
            EpicsMoveable.doStop(self)
