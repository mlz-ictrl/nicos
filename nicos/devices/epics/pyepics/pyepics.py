# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
from time import monotonic
import numbers

import epics

from nicos import session
from nicos.commands import helparglist, hiddenusercommand
from nicos.core import POLLER, SIMULATION, CommunicationError, \
    ConfigurationError, DeviceMixinBase, HasLimits, Moveable, Override, \
    Param, Readable, anytype, floatrange, none_or, pvname, status
from nicos.core.mixins import HasWindowTimeout
from nicos.devices.epics.status import SEVERITY_TO_STATUS, STAT_TO_STATUS
from nicos.utils import HardwareStub

# ca.clear_cache() only works from the main thread
if not isinstance(threading.current_thread(), threading._MainThread):
    raise ImportError('the nicos.devices.epics module must be first '
                      'imported from the main thread')


# Clear the EPICS cache of CA connections, which are (somehow) kept across
# subprocesses.  This call ensures fresh connections for each process, since
# it is called once at import time, before epics objects can be created.
try:
    epics.ca.clear_cache()
    epics.ca.initialize_libca()
except epics.ca.ChannelAccessException as err:
    if hasattr(err, 'args'):
        msg = err.args[0]
    else:
        msg = 'error in epics channel access setup'
    raise ImportError(msg) from None

__all__ = [
    'EpicsDevice', 'EpicsReadable', 'EpicsStringReadable',
    'EpicsMoveable', 'EpicsAnalogMoveable', 'EpicsDigitalMoveable',
    'EpicsWindowTimeoutDevice',
]

# Map PV data type to NICOS value type.
FTYPE_TO_VALUETYPE = {
    0: str,
    1: int,
    2: float,
    3: int,
    4: bytes,
    5: int,
    6: float,

    14: str,
    15: int,
    16: float,
    17: int,
    18: bytes,
    19: int,
    20: float,

    28: str,
    29: int,
    30: float,
    31: int,
    32: bytes,
    33: int,
    34: float,
}


@hiddenusercommand
@helparglist('name[, as_string, count, as_numpy, timeout]')
def pvget(name, as_string=False, count=None, as_numpy=True,
          timeout=5.0):
    return epics.caget(name, as_string, count, as_numpy, timeout=timeout)


@hiddenusercommand
@helparglist('name, value[, wait, timeout]')
def pvput(name, value, wait=False, timeout=60):
    epics.caput(name, value, wait, timeout)


class EpicsDevice(DeviceMixinBase):
    """
    Basic EPICS device.
    """

    hardware_access = True
    valuetype = anytype

    parameters = {
        'epicstimeout': Param('Timeout for getting EPICS PVs',
                              type=none_or(floatrange(0.1, 60)),
                              default=3.0, userparam=False),
    }

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

            # When there are standard names for PVs (see motor record), the PV
            # names may be derived from some prefix. To make this more
            # flexible, the pv_parameters are obtained via a method that can
            # be overridden in subclasses.
            pv_parameters = self._get_pv_parameters()
            for pvparam in pv_parameters:

                # Retrieve the actual PV-name from (potentially overridden)
                # method
                pvname = self._get_pv_name(pvparam)
                if not pvname:
                    raise ConfigurationError(self, 'PV for parameter %s was '
                                                   'not found!' % pvparam)
                pv = self._pvs[pvparam] = epics.pv.PV(
                    pvname, connection_timeout=self.epicstimeout)
                pv.connect()
                if not pv.wait_for_connection(timeout=self.epicstimeout):
                    raise CommunicationError(self, 'could not connect to PV %r'
                                             % pvname)

                self._pvctrls[pvparam] = pv.get_ctrlvars() or {}

            if session.sessiontype == POLLER:
                self._register_pv_callbacks()
        else:
            for pvparam in self._get_pv_parameters():
                self._pvs[pvparam] = HardwareStub(self)
                self._pvctrls[pvparam] = {}

    def _register_pv_callbacks(self):
        pass

    def _get_pv_parameters(self):
        # The default implementation of this method simply returns the
        # pv_parameters set
        return set()

    def _get_pv_name(self, pvparam):
        # In the default case, the name of a PV-parameter is stored in ai
        # parameter. This method can be overridden in subclasses in case the
        # name can be derived using some other information.
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        # Return the status and the affected pvs in case the status is not OK
        mapped_status, affected_pvs = self._get_mapped_epics_status()

        status_message = 'Affected PVs: ' + ', '.join(
            affected_pvs) if mapped_status != status.OK else ''
        return mapped_status, status_message

    def _get_mapped_epics_status(self):
        # Checks the status and severity of all the associated PVs.
        # Returns the worst status (error prone first) and
        # a list of all associated pvs having that error
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        status_map = {}
        for name in self._pvs:
            epics_status = self._get_pvctrl(name, 'status', update=True)
            epics_severity = self._get_pvctrl(name, 'severity')

            mapped_status = STAT_TO_STATUS.get(epics_status, None)

            if mapped_status is None:
                mapped_status = SEVERITY_TO_STATUS.get(
                    epics_severity, status.UNKNOWN)

            status_map.setdefault(mapped_status, []).append(
                self._get_pv_name(name))

        return max(status_map.items())

    def _setMode(self, mode):
        # Remove the PVs on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            for key in self._pvs:
                self._pvs[key] = HardwareStub(self)

    def _get_pv(self, pvparam, as_string=False, count=None, use_monitor=True):
        # since NICOS devices can be accessed from any thread, we have to
        # ensure that the same context is set on every thread
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()
        result = self._pvs[pvparam].get(timeout=self.epicstimeout,
                                        as_string=as_string,
                                        count=count,
                                        use_monitor=use_monitor)
        if result is None:  # timeout
            raise CommunicationError(self, 'timed out getting PV %r from EPICS'
                                     % self._get_pv_name(pvparam))
        return result

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        if update:
            if epics.ca.current_context() is None:
                epics.ca.use_initial_context()

            try:
                self._pvctrls[pvparam] = self._pvs[pvparam].get_ctrlvars()
            except Exception:
                self._pvctrls[pvparam] = {}

        result = self._pvctrls[pvparam]
        if result is None:
            return default
        return result.get(ctrl, default)

    def _put_pv(self, pvparam, value, wait=False):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        self._pvs[pvparam].put(value, wait=wait, timeout=self.epicstimeout)

    def _put_pv_checked(self, pvparam, value, wait=False, update_rate=0.1,
                        timeout=60, precision=0):
        """
        Write a PV and block the session until it has been verified that the PV
        has actually changed on the EPICS side. In case of a numeric PV, it is
        also possible to specify the precision. This is for example needed for
        the motor record, where the target value can only be set up to the
        resolution defined in the MRES field.
        """
        def isEqualNum(pv, value, precision):
            return abs(pv.get()- value) <= precision

        def isEqualOther(pv, value, precision):
            return pv.get() == value

        if isinstance(value, numbers.Number):
            isEqual = isEqualNum
        else:
            isEqual = isEqualOther

        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        pv = self._pvs[pvparam]

        pv.put(value, wait=wait, timeout=self.epicstimeout)

        start = monotonic()
        while not isEqual(pv, value, precision):
            if monotonic() - start > timeout:
                raise CommunicationError('Timeout in setting %s' % pv.pvname)
            session.delay(update_rate)

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1, timeout=60):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()

        pv = self._pvs[pvparam]

        pv.put(value, use_complete=True)

        start = monotonic()
        while not pv.put_complete:
            if monotonic() - start > timeout:
                raise CommunicationError('Timeout in setting %s' % pv.pvname)
            session.delay(update_rate)


class EpicsReadable(EpicsDevice, Readable):
    """
    Handles EPICS devices that can only read a value.
    """

    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, userparam=False),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def _get_pv_parameters(self):
        return {'readpv'}

    def doInit(self, mode):
        if mode != SIMULATION:
            self.valuetype = FTYPE_TO_VALUETYPE.get(self._pvs['readpv'].ftype,
                                                    anytype)

    def doReadUnit(self):
        return self._get_pvctrl('readpv', 'units',
                                self._config.get('unit', ''))

    def doRead(self, maxage=0):
        return self._get_pv('readpv')


class EpicsStringReadable(EpicsReadable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

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
        'unit': Override(mandatory=False),
        'target': Override(volatile=True),
    }

    def _get_pv_parameters(self):
        """
        Overriden from EpicsDevice. If the targetpv parameter is specified,
        the PV-object should be created accordingly. Otherwise, just return
        the mandatory pv_parameters.
        """
        if self.targetpv:
            return {'readpv', 'writepv', 'targetpv'}

        return {'readpv', 'writepv'}

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        intype = FTYPE_TO_VALUETYPE.get(self._pvs['readpv'].ftype, anytype)
        outtype = FTYPE_TO_VALUETYPE.get(self._pvs['writepv'].ftype, anytype)
        if intype is not anytype and intype != self.valuetype:
            raise ConfigurationError(self, 'Input PV %r does not have the '
                                           'correct data type' % self.readpv)
        if outtype is not anytype and outtype != self.valuetype:
            raise ConfigurationError(self, 'Output PV %r does not have the '
                                           'correct data type' % self.writepv)

        if self.targetpv:
            target_type = FTYPE_TO_VALUETYPE.get(
                self._pvs['targetpv'].ftype, anytype)

            if target_type is not anytype and target_type != self.valuetype:
                raise ConfigurationError(
                    self, 'Target PV %r does not have the '
                          'correct data type' % self.targetpv)

    def doReadUnit(self):
        return self._get_pvctrl('readpv', 'units', '')

    def doReadTarget(self):
        """
        IOCs commonly provide a read-back of the set-point according to the
        device (targetpv). When this read-back is not present then the writepv
        should be read instead.
        """
        if self.targetpv:
            return self._get_pv('targetpv')

        return self._get_pv('writepv')

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, target):
        self._put_pv('writepv', target)

    def doStop(self):
        self.doStart(self.doRead(0))


class EpicsStringMoveable(EpicsMoveable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

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

    def doReadAbslimits(self):
        absmin = self._get_pvctrl('writepv', 'lower_ctrl_limit', -1e308)
        absmax = self._get_pvctrl('writepv', 'upper_ctrl_limit', 1e308)
        return (absmin, absmax)


class EpicsWindowTimeoutDevice(HasWindowTimeout, EpicsAnalogMoveable):
    """
    Analog moveable with window timeout.
    """


class EpicsDigitalMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read an integer value.
    """
    valuetype = int

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }
