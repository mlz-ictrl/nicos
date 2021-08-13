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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michael Wedel <michael.wedel@esss.se>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
This module contains ESS specific EPICS developments.
"""
from nicos.core import Attach, CanDisable, ConfigurationError, Device, \
    InvalidValueError, Override, Param, anytype, dictwith, pvname, \
    usermethod
from nicos.devices.abstract import MappedMoveable

from nicos_ess.devices.epics.base import EpicsAnalogMoveableEss, \
    EpicsDeviceEss, EpicsDigitalMoveableEss


class EpicsMappedMoveable(MappedMoveable, EpicsDigitalMoveableEss):
    """
    EPICS based implementation of MappedMoveable. Useful for PVs that contain
    enums or bools.
    """

    parameters = {
        'ignore_stop': Param(
            'Whether to do anything when stop is called',
            type=bool, default=False, userparam=False),
    }

    def doInit(self, mode):
        EpicsDigitalMoveableEss.doInit(self, mode)
        MappedMoveable.doInit(self, mode)

    def doReadTarget(self):
        target_value = EpicsDigitalMoveableEss.doReadTarget(self)

        # If this is from EPICS, it needs to be mapped, otherwise not
        if self.targetpv:
            return self._mapReadValue(target_value)

        return target_value

    def _readRaw(self, maxage=0):
        return EpicsDigitalMoveableEss.doRead(self, maxage)

    def _startRaw(self, target):
        EpicsDigitalMoveableEss.doStart(self, target)

    def doStop(self):
        if not self.ignore_stop:
            EpicsDigitalMoveableEss.doStop(self)

    def doRead(self, maxage=0):
        return MappedMoveable.doRead(self, maxage)

    def doStart(self, value):
        MappedMoveable.doStart(self, value)


class EpicsMappedFloatMoveable(EpicsMappedMoveable):
    valuetype = float
    relax_mapping = True


class EpicsAnalogMoveableWithUnitsSelector(EpicsAnalogMoveableEss):
    """
    A device where the units are the value of another PV.
    """

    parameter_overrides = {
        'unit': Override(mandatory=False, userparam=False, volatile=True),
    }

    attached_devices = {
        'units': Attach('Units', EpicsMappedMoveable),
    }

    def doPoll(self, n, maxage):
        self._pollParam('unit')

    def doReadUnit(self):
        return str(self._attached_units.doRead())

    def doWriteUnit(self, value):
        try:
            self._attached_units.doStart(value)
        except InvalidValueError as error:
            positions = ', '.join(repr(pos)
                                  for pos in self._attached_units.mapping)
            raise InvalidValueError(self, f'{value} is an invalid unit choice '
                                          f'for this device; valid choices are '
                                          f'{positions}') from error


class HasDisablePv(CanDisable):
    """
    A mixin that can be used with EPICS based devices.

    Devices that inherit this mixin get a new property that indicates
    whether the device is enabled (that may mean different things
    in different devices):

        dev.isEnabled

    To enable or disable, use the provided methods:

        dev.enable()
        dev.disable()

    The link to EPICS is configured via the switchpvs and switchstates
    parameters. The former defines which PV to read for the status
    information as well as which one to write to when using the methods.
    The latter defines what values the PV accepts for enable and disable
    respectively.
    """

    parameters = {
        'switchstates':
            Param('Map of boolean states to underlying type',
                  type=dictwith(enable=anytype, disable=anytype),
                  userparam=False),
        'switchpvs':
            Param('Read and write pv for enabling and disabling the device',
                  type=dictwith(read=pvname, write=pvname),
                  userparam=False)
    }

    def _get_pv_parameters(self):
        # Use colon prefix to prevent name clashes with
        # PVs specified in EpicsDevice.param
        switch_pvs = {'switchpv:' + pv for pv in self.switchpvs}

        return super()._get_pv_parameters() | switch_pvs

    def _get_pv_name(self, pvparam):
        components = pvparam.split(':', 1)

        if len(components) == 2 and components[0] == 'switchpv':
            return self.switchpvs[components[1]]

        return super()._get_pv_name(pvparam)

    @property
    def isEnabled(self):
        """
        True if the device is switched on.
        """
        raw_value = self._get_pv('switchpv:read')

        if raw_value not in self.switchstates.values():
            raise ConfigurationError('State by attached switch device not '
                                     'recognized.')

        return raw_value == self.switchstates['enable']

    @usermethod
    def enable(self):
        """
        Switch the device on (writes the 'enable' of switchstates map to the
        write-pv specified in switchpvs).
        """
        if not self.isEnabled:
            self._put_pv('switchpv:write', self.switchstates['enable'])
        else:
            self.log.info('Device is already switched on')

    @usermethod
    def disable(self):
        """
        Switch the device off (writes the 'disable' of switchstates map to the
        write-pv specified in switchpvs).
        """
        if self.isEnabled:
            self._put_pv('switchpv:write', self.switchstates['disable'])
        else:
            self.log.info('Device is already disabled')


class EpicsCommandReply(EpicsDeviceEss, Device):
    """
    Device to directly control devices connected to
    the asyn controller via EPICS.

    This device can issue commands to the asyn controller
    which in turn can operate the attached devices to the
    controller. The commands issued should adhere to the
    policies and syntax of the asyn controller.

    To do this via EPICS, two pvs can be provided:

    commandpv - PV that forwards the command to be executed
                to the controller
    replypv - PV that stores the reply generated from
              the execution of the command
    """

    parameters = {
        'commandpv': Param('PV to issue commands to the asyn controller',
                           type=pvname, mandatory=True, settable=False,
                           userparam=False),
        'replypv': Param('PV that stores the reply generated from execution',
                         type=pvname, mandatory=False, settable=False,
                         userparam=False),
    }

    def _get_pv_parameters(self):
        pvs = {'commandpv'}

        if self.replypv:
            pvs.add('replypv')

        return pvs

    @usermethod
    def execute(self, command):
        """
        Issue and execute the provided command
        Returns the reply if the replypv is set
        """
        # Send the command to the commandpv
        self._put_pv_blocking('commandpv', command)

        # If reply PV is set, return it's output
        return self._get_pv('replypv') if self.replypv else ''
