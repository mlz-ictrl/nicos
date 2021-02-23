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
This module contains some classes for NICOS - EPICS integration.
"""
import time

from nicos import session
from nicos.core import POLLER, SIMULATION, ConfigurationError,\
    DeviceMixinBase, HasLimits, Moveable, Override, Param, Readable, anytype,\
    floatrange, none_or, pvname, status
from nicos.devices.abstract import MappedMoveable
from nicos.utils import HardwareStub

from nicos_ess.devices.epics.pva.p4p import PvaWrapper

__all__ = [
    'EpicsDevice', 'EpicsReadable', 'EpicsStringReadable',
    'EpicsMoveable', 'EpicsAnalogMoveable', 'EpicsDigitalMoveable',
    'EpicsMonitorMixin'
]


class EpicsMonitorMixin(DeviceMixinBase):
    pv_status_parameters = set()
    _epics_subscriptions = set()
    _cache_relations = {'readpv': 'value'}
    _statuses = {}

    def _register_pv_callbacks(self):
        self._epics_subscriptions = set()
        self._statuses = {}

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
        # Override for custom subscriptions
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback)

    def value_change_callback(self, name, param, value, severity, message,
                              **kwargs):
        self.log.debug(
            f'{name} [{param}]: value cb with {value} {severity} {message}!')
        # TODO: if no cache key then what should we do with it?
        cache_key = self._get_cache_relation(param) or name
        self._cache.put(self._name, cache_key, value, time.time())
        self._set_status(name, param, severity, message)

    def status_change_callback(self, name, param, value, severity, message,
                               **kwargs):
        self.log.debug(
            f'{name} [{param}]: status cb with {value} {severity} {message}')
        self._set_status(name, param, severity, message)
        current_status = self.doStatus()
        self._cache.put(self._name, 'status', current_status, time.time())

    def connection_change_callback(self, name, pvparam, is_connected, **kwargs):
        if is_connected:
            self.log.debug(f'{name} connected!')
            # Clear any readpv status.
            if pvparam == 'readpv':
                self._set_status(name, 'readpv', status.OK, '')
        else:
            self.log.warn(f'{name} disconnected!')
            # Put readpv into error state.
            if pvparam == 'readpv':
                self._set_status(name, 'readpv', status.ERROR, 'disconnected')

    def _get_cache_relation(self, param):
        # Returns the cache key associated with the parameter.
        return self._cache_relations.get(param, None)

    def _get_status_parameters(self):
        # Returns the parameters which indicate "movement" is happening.
        return self.pv_status_parameters

    def _set_status(self, name, param, severity, message):
        self._statuses[param] = (name, severity, message)

    def doStatus(self, maxage=0):
        # For most devices we only care about the status of the read PV
        if 'readpv' in self._statuses:
            pvname, severity, message = self._statuses['readpv']
        else:
            pvname = self._get_pv_name('readpv')
            severity, message = self._epics_wrapper.get_alarm_status(pvname,
                                    self.epicstimeout)
        if severity != status.OK:
            return severity, f'issue with {pvname}: {message}'
        return severity, ''

    def doShutdown(self):
        for sub in self._epics_subscriptions:
            sub.close()


class EpicsDevice(DeviceMixinBase):
    hardware_access = True
    valuetype = anytype

    parameters = {
        'epicstimeout': Param('Timeout for getting EPICS PVs',
                              type=none_or(floatrange(0.1, 60)),
                              userparam=False, mandatory=False, default=1.0),
    }
    parameter_overrides = {
        # Hide the parameters that are irrelevant when using monitors.
        'maxage': Override(userparam=False, settable=False),
        'pollinterval': Override(userparam=False, settable=False),
    }

    # A set of all parameters that indicate PV names.  Since PVs are very
    # limited, an EpicsDevice is expected to use many different PVs a lot
    # of times.
    pv_parameters = set()

    # This will store PV objects for each PV param.
    _pvs = {}
    _epics_wrapper = None

    def doPreinit(self, mode):
        self._epics_wrapper = PvaWrapper()

        # Don't create PVs in simulation mode
        self._pvs = {}

        if mode != SIMULATION:
            for pvparam in self._get_pv_parameters():
                # Retrieve the actual PV name
                pvname = self._get_pv_name(pvparam)
                if not pvname:
                    raise ConfigurationError(self, 'PV for parameter %s was '
                                                   'not found!' % pvparam)
                # Check pv exists - throws if cannot connect
                self._epics_wrapper.connect_pv(pvname, self.epicstimeout)
                self._pvs[pvparam] = pvname
            self._register_pv_callbacks()
        else:
            for pvparam in self._get_pv_parameters():
                self._pvs[pvparam] = HardwareStub(self)

    def _register_pv_callbacks(self):
        pass

    def _get_pv_parameters(self):
        # The default implementation of this method simply returns the
        # pv_parameters set
        return self.pv_parameters

    def _get_pv_name(self, pvparam):
        # In the default case, the name of a PV-parameter is stored in a
        # parameter. This method can be overridden in subclasses in case the
        # name can be derived using some other information.
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        # For most devices we only care about the status of the read PV
        pvname = self._get_pv_name('readpv')
        severity, msg = self._epics_wrapper.get_alarm_status(pvname,
                            timeout=self.epicstimeout)
        if severity in [status.ERROR, status.WARN]:
            return severity, msg
        return status.OK, msg

    def _setMode(self, mode):
        # remove the PVs on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            for key in self._pvs:
                self._pvs[key] = HardwareStub(self)

    def _get_pv(self, pvparam, as_string=False):
        return self._epics_wrapper.get_pv_value(self._pvs[pvparam],
                                                timeout=self.epicstimeout,
                                                as_string=as_string)

    def _put_pv(self, pvparam, value, wait=False):
        self._epics_wrapper.put_pv_value(self._pvs[pvparam], value, wait=wait,
                                         timeout=self.epicstimeout)

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1, timeout=60):
        self._epics_wrapper.put_pv_value_blocking(self._pvs[pvparam], value,
                                                  update_rate, timeout)


class EpicsReadable(EpicsMonitorMixin, EpicsDevice, Readable):
    """
    Handles EPICS devices that can only read a value.
    """
    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, userparam=False),
    }

    parameter_overrides = {
        # Units are set by EPICS, so cannot be changed
        'unit': Override(mandatory=False, settable=False),
    }

    pv_parameters = {
        'readpv': '',
        'units': 'EGU',
    }

    _cache_relations = {
        'readpv': 'value',
        'units': 'unit',
    }

    parameter_overrides = {
        # Units are set by EPICS, so cannot be changed
        'unit': Override(mandatory=False, settable=False),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        self.valuetype = self._epics_wrapper.get_pv_type(self._pvs['readpv'],
                                                         self.epicstimeout)

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def _get_pv_parameters(self):
        return set(self.pv_parameters.keys())

    def _get_pv_name(self, pvparam):
        if hasattr(self, pvparam):
            return getattr(self, pvparam)
        stem = getattr(self, 'readpv')
        return '.'.join([stem, self.pv_parameters[pvparam]])


class EpicsStringReadable(EpicsReadable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

    pv_parameters = {'readpv'}

    _cache_relations = {
        'readpv': 'value',
    }

    def _get_pv_parameters(self):
        return self.pv_parameters

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsMoveable(EpicsMonitorMixin, EpicsDevice, Moveable):
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
        # Units are set by EPICS, so cannot be changed
        'unit': Override(mandatory=False, settable=False),
        'target': Override(volatile=True),
    }

    pv_parameters = {'readpv', 'writepv',}

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target',
    }

    def _get_pv_parameters(self):
        if self.targetpv:
            return self.pv_parameters | {'targetpv'}

        return self.pv_parameters

    def _get_pv_name(self, pvparam):
        if hasattr(self, pvparam):
            return getattr(self, pvparam)
        stem = getattr(self, 'readpv')
        return '.'.join([stem, self.pv_parameters[pvparam]])

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        in_type = self._epics_wrapper.get_pv_type(self._pvs['readpv'],
                                                  self.epicstimeout)
        out_type = self._epics_wrapper.get_pv_type(self._pvs['writepv'],
                                                   self.epicstimeout)
        if in_type != self.valuetype:
            raise ConfigurationError(self, 'Input PV %r does not have the '
                                           'correct data type' % self.readpv)
        if out_type != self.valuetype:
            raise ConfigurationError(self, 'Output PV %r does not have the '
                                           'correct data type' % self.writepv)
        if self.targetpv:
            target_type = self._epics_wrapper.get_pv_type(self._pvs['targetpv'],
                                                          self.epicstimeout)
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

    pv_parameters = {'readpv', 'writepv'}

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target',
    }

    def _get_pv_parameters(self):
        return self.pv_parameters

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsAnalogMoveable(HasLimits, EpicsMoveable):
    """
    Handles EPICS devices which can set and read a floating value.
    """
    valuetype = float

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
    }

    pv_parameters = {
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
        params = set(self.pv_parameters.keys())

        if self.targetpv:
            return params | {'targetpv'}

        return params

    def _get_pv_name(self, pvparam):
        if hasattr(self, pvparam):
            return getattr(self, pvparam)
        stem = getattr(self, 'readpv')
        return '.'.join([stem, self.pv_parameters[pvparam]])


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

    parameter_overrides = {
        # Units are set by EPICS, so cannot be changed
        'unit': Override(mandatory=False, settable=False),
        # Mapping values are usual read from EPICS
        'mapping': Override(mandatory=False, settable=True, userparam=False)
    }

    pv_parameters = {'readpv', 'writepv'}

    def _subscribe(self, change_callback, pvname, pvparam):
        # Override for custom subscriptions
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback,
                                             as_string=True)

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        if session.sessiontype != POLLER:
            choices = self._epics_wrapper.get_value_choices(
                self._get_pv_name('readpv'), self.epicstimeout)
            # Existing mapping is fixed, so must create and replace
            new_mapping = {}
            for i, choice in enumerate(choices):
                new_mapping[choice] = i
            self.mapping = new_mapping

        MappedMoveable.doInit(self, mode)

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)

    def doStart(self, target):
        self._put_pv('writepv', target)
