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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""
This module contains some classes for NICOS - EPICS integration.
"""

import threading

from nicos.core import CommunicationError, ConfigurationError, \
    DeviceMixinBase, HasLimits, Moveable, Override, Param, Readable, \
    SIMULATION, anytype, floatrange, none_or, status
from nicos.core.mixins import HasWindowTimeout
from nicos.utils import HardwareStub
from time import sleep

# ca.clear_cache() only works from the main thread
if not isinstance(threading.currentThread(), threading._MainThread):
    raise ImportError('the nicos.devices.epics module must be first '
                      'imported from the main thread')

epics = __import__('epics')

# Clear the EPICS cache of CA connections, which are (somehow) kept across
# subprocesses.  This call ensures fresh connections for each process, since
# it is called once at import time, before epics objects can be created.
epics.ca.clear_cache()

__all__ = [
    'EpicsDevice', 'EpicsReadable', 'EpicsMoveable',
    'EpicsAnalogMoveable', 'EpicsDigitalMoveable',
    'EpicsWindowTimeoutDevice',
]

pvname = str  # TODO: create validator

# Map PV data type to NICOS value type.
FTYPE_TO_VALUETYPE = {
    0: str,
    1: int,
    2: float,
    3: int,
    4: bytes,
    5: int,
    6: float,
    20: float,
}


class EpicsDevice(DeviceMixinBase):
    """
    Basic EPICS device.
    """

    hardware_access = True
    valuetype = anytype

    parameters = {
        'epicstimeout': Param('Timeout for getting EPICS PVs',
                              type=none_or(floatrange(0.1, 60)),
                              default=1.0),
    }

    # A set of all parameters that indicate PV names.  Since PVs are very
    # limited, an EpicsDevice is expected to use many different PVs a lot
    # of times.
    pv_parameters = set()

    # This will store PV objects for each PV param.
    _pvs = {}
    _pvctrls = {}

    def doPreinit(self, mode):
        # Don't create PVs in simulation mode
        self._pvs = {}
        self._pvctrls = {}
        if mode != SIMULATION:
            # in case we get started in a thread, make sure to use the global
            # CA context in that thread
            if epics.ca.current_context() is None:
                epics.ca.use_initial_context()

            # When there are standard names for PVs (see motor record), the PV names
            # may be derived from some prefix. To make this more flexible, the pv_parameters
            # are obtained via a method that can be overridden in subclasses.
            pv_parameters = self._get_pv_parameters()
            for pvparam in pv_parameters:

                # Retrieve the actual PV-name from (potentially overridden) method
                pvname = self._get_pv_name(pvparam)
                pv = self._pvs[pvparam] = epics.pv.PV(pvname, connection_timeout=self.epicstimeout)
                pv.connect()
                if not pv.wait_for_connection(timeout=self.epicstimeout):
                    raise CommunicationError(self, 'could not connect to PV %r'
                                             % pvname)

                self._pvctrls[pvparam] = pv.get_ctrlvars() or {}

    def _get_pv_parameters(self):
        # The default implementation of this method simply returns the pv_parameters set
        return self.pv_parameters

    def _get_pv_name(self, pvparam):
        # In the default case, the name of a PV-parameter is stored in a parameter.
        # This method can be overridden in subclasses in case the name can be derived
        # using some other information.
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        return status.OK, ''

    def _setMode(self, mode):
        super(EpicsDevice, self)._setMode(mode)
        # remove the PVs on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            for key in self._pvs:
                self._pvs[key] = HardwareStub(self)

    def _get_pv(self, pvparam):
        # since NICOS devices can be accessed from any thread, we have to
        # ensure that the same context is set on every thread
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()
        result = self._pvs[pvparam].get(timeout=self.epicstimeout)
        if result is None:  # timeout
            raise CommunicationError(self, 'timed out getting PV %r from EPICS'
                                     % getattr(self, pvparam))
        return result

    def _get_pvctrl(self, pvparam, ctrl, default=None):
        return self._pvctrls[pvparam].get(ctrl, default)

    def _put_pv(self, pvparam, value, wait=True):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        self._pvs[pvparam].put(value, wait=wait, timeout=self.epicstimeout)

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        pv = self._pvs[pvparam]

        pv.put(value, use_complete=True)

        while not pv.put_complete:
            sleep(update_rate)


class EpicsReadable(EpicsDevice, Readable):
    """
    Handles EPICS devices that can only read a value.
    """

    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True),
    }

    pv_parameters = set(('readpv',))

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self.valuetype = FTYPE_TO_VALUETYPE.get(self._pvs['readpv'].ftype,
                                                    anytype)

    def doReadUnit(self):
        pvunit = self._get_pvctrl('readpv', 'units', '')
        if not pvunit and 'unit' in self._config:
            return self._config['unit']
        return pvunit

    def doRead(self, maxage=0):
        return self._get_pv('readpv')


class EpicsMoveable(EpicsDevice, Moveable):
    """
    Handles EPICS devices which can set and read a value.
    """

    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True),
        'writepv': Param('PV for writing device target',
                         type=pvname, mandatory=True),
    }

    pv_parameters = set(('readpv', 'writepv'))

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doInit(self, mode):
        intype = FTYPE_TO_VALUETYPE.get(self._pvs['readpv'].ftype, anytype)
        outtype = FTYPE_TO_VALUETYPE.get(self._pvs['writepv'].ftype, anytype)
        if intype != self.valuetype:
            raise ConfigurationError(self, 'Input PV %r does not have the '
                                           'correct data type' % self.readpv)
        if outtype != self.valuetype:
            raise ConfigurationError(self, 'Output PV %r does not have the '
                                           'correct data type' % self.writepv)

    def doReadUnit(self):
        return self._get_pvctrl('readpv', 'units', '')

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        self._put_pv('writepv', value)

    def doStop(self):
        self.doStart(self.doRead())


class EpicsAnalogMoveable(HasLimits, EpicsMoveable):
    """
    Handles EPICS devices which can set and read a floating value.
    """

    valuetype = float

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
    }

    def doReadAbslimits(self):
        absmin = self._get_pvctrl('writepv', 'lower_ctrl_limit', -1e308)
        absmax = self._get_pvctrl('writepv', 'upper_ctrl_limit', 1e308)
        return (absmin, absmax)


class EpicsWindowTimeoutDevice(HasWindowTimeout, EpicsAnalogMoveable):
    """
    Analog moveable with window timeout.
    """
    pass


class EpicsDigitalMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read an integer value.
    """
    valuetype = int
