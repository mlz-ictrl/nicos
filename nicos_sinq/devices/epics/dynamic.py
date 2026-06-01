# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
"""
Meta devices that manages the creation of dynamic EPICS devices.
Dynamic EPICS devices are devices which may not always physically
be available, but has an EPICS driver level support for detecting
if they are connected or not. This can be via:
1. Asyn natively, through the Asyn record connecting to a lower level
   port created with for example AsynIPPortdriver.
   Furthermore this implementation also checks the status of common
   PVs specified on common PV parameter names, e.g. readpv, and write pv.
   This status check is needed for serial devices that are connected via
   a terminal server. With native IP devices it's not strictly required,
   but doesn't hurt.
2. MasterMacs MCU through the high level EPICS motor driver with
   support for detecting if individual axes are connected.
"""
from nicos import session
from nicos.core import DeviceMixinBase, status
from nicos.core import Readable
from nicos.core import Param, MASTER, Override
from nicos.core.errors import ProgrammingError
from nicos.core.params import listof, dictof, tupleof, anytype, nicosdev
from nicos.devices.epics.base import EpicsDevice, EpicsReadable
from nicos.devices.epics.tools import epics_get
from nicos.core.errors import ConfigurationError


class DynamicMixin(DeviceMixinBase):
    """Mixin class for dynamic devices
    """

    def doInit(self, mode):
        self.log.debug('Initializing dynamic device')
        self._dyndevices = []
        if mode == MASTER:
            # Dynamic devices can not be created in the poller.
            self.create_devices()

    def _create_devices(self):
        """Left to implement for the actual device class, usually should call
        _add_device in one way or another.
        """
        raise ProgrammingError('_create_devices not implemented')

    def _add_device(self, name, cls, **devparams):
        """Internal method for adding devices. Inspired by SecNodeDevice.
        :param name: name of the devices to create
        :param cls: path to the class that should be instantiated
        :param devparam: dictionary of the device's parameters
        """
        if name not in session.configured_devices:
            # find setup of this device, inspired by SecNodeDevice
            result = session.getSetupInfo()
            this_setupname = None
            for setupname in session.loaded_setups:
                info = result.get(setupname, None)
                if info and self.name in info['devices']:
                    this_setupname = setupname
                    break
            else:
                raise ConfigurationError('Can not locate current setup,\
                        this should not happen.')
        else:
            self.log.error('Could not create dynamic epics device %s, '\
                    'device name already exists in another setup.', name)
            return
        # Use monitor for callbacks and create them in the daemon,
        # the device doesn't exist in the Poller
        devparams.update(
                {
                    'monitor': True,
                    'cbs_in_daemon': True,
                    'visibility': ('devlist', 'metadata', 'namespace')
                }
            )
        # Actually create the device.
        self.log.debug('Creating %s in %s', name, this_setupname)
        self.log.debug('devparams %s', devparams)
        session.configured_devices[name] = (cls, devparams)
        session.dynamic_devices[name] = this_setupname
        session.createDevice(name, recreate=True, explicit=True)
        self._dyndevices.append(name)

    def _shutdown_device(self, name):
        """
        Shut down a single of the created devices.
        :param name: name of the dynamic device to shut down
        """
        if name in self._dyndevices:
            self.log.debug('Shutting down %s', name)
            session.destroyDevice(name)
            del session.dynamic_devices[name]
            del session.configured_devices[name]

    def doShutdown(self):
        """
        Shutdown all dynamic devices as part of shutting down this device.
        """
        for name in self._dyndevices:
            self._shutdown_device(name)


class AsynDevice(DynamicMixin, EpicsReadable):
    """
    A dynamic Asyn device, utilizing the Asyn record interface.
    This devices dynamically creates devices specified in deviceconfig
    depending on if the Asyn record signals that it is connected.

    This creates ANY device class listed, since these classes doesn't
    necessarily inherit from 'autodevice' the autodevice design pattern can not
    be used.
    """
    parameters = {
            # readpv should be specified as the base name of the Asyn Record
            'devicesconfig': Param('Nested dictionary, each entry contains all configuration '
                ' needed for one device', type=dictof(tupleof(nicosdev, str), dictof(str, anytype)),
                mandatory=True, settable=False, userparam=False),
            }

    # connect is used in doRead
    _record_fields = {
        'connect' : 'CNCT'
    }

    # The val field contains nothing, use connect field for reading
    _cache_relations = {'connect': 'value'}

    def doInit(self, mode):
        EpicsReadable.doInit(self, mode)
        DynamicMixin.doInit(self, mode)

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically concatenates asyn record PV with a
        dot and the field name.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        # Return base record name as readpv, doing so we can use the
        # default doStatus implementation
        if pvparam == 'readpv':
            return self.readpv

        # Map parameter name to field
        asyn_field = self._record_fields.get(pvparam)

        if asyn_field is not None:
            return '.'.join((self.readpv, asyn_field))

        raise ProgrammingError(
                'The field corresponding to %s is not configured' % pvparam)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in asyn record.

        Currently only the base PV and 1 field in the asyn record is supported

        :return: List of PV aliases.
        """
        return ['readpv'] + list(self._record_fields.keys())

    def doRead(self, maxage=0):
        """
        The asyn record's VAL field does nothing, so instead of using readpv,
        we return the value of the .CNCT field (i.e. connection status) as a string.

        :return: String of connection status
        """
        return self._get_pv('connect', as_string=True)

    def create_devices(self):
        """
        Create devices dynamically if asyn record signals that the device
        is connected. Additionally take into account the status of the
        underlying device record. Status is LINK indicating the query of the
        hardware failed, similarly COMM indicated that communication failed.
        This is necessary to support devices that are connected via serial to
        tcp/ip converter box (e.g. a Moxa), where the Converter box may still
        be online but not the serial device itself.
        """
        link_status = self.read(0)
        self.log.debug('In create_devices link_status is %s', link_status)
        # The connect PV indicates that this device is online.
        if link_status == 'Connect':
            # Create number of kwargs devices
            for (name, cls), kwargs in self.devicesconfig.items():
                # For things connected via Moxas we also need to check
                # status invalid and severity LINK. (It doesn't hurt to do
                # so in case of being a pure tcp/ip device either)
                num_broken = 0
                # check some common pvparam names.
                for pv in ['readpv', 'writepv']:
                    if pv in kwargs:
                        stat = epics_get(kwargs[pv] + ".STAT")
                        self.log.debug('%s has status %s', kwargs[pv], stat)
                        if stat in [b'LINK', b'COMM']:
                            # The device is probably disconnected from a moxa
                            num_broken += 1
                if num_broken == 0:
                    self._add_device(name, cls, **kwargs)

class MasterMacsNode(DynamicMixin, EpicsDevice, Readable):
    """Dynamic MasterMacs node

    Represents one can-bus station, typically installed at every
    sample position.

    * They rely on a SinqMotor specific 'connected' PV per motor on the bus.
        - Each motor may be connected or disconnected at any time.
        - Some hardware restrictions apply here:
        As of 2026-04-02: Nanotec motors are not able to be dynamically discovered.
        Nanotec does not implement the CAN bus standard correctly/fully.
        What has been tested and is working are Technosoft motors.

    * The motors are completely self configured and need no extra configuration.
    """

    parameters = {
            'pvprefix': Param('PV prefix to use in search for devices',
                type=str, mandatory=True, settable=False, userparam=False),
            'pvsuffixes': Param('PV suffixes to search for',
                type=listof(str), mandatory=True, settable=False, userparam=False),
            '_connected_list': Param('List of currently connected devices',
                type=listof(str), mandatory=False, settable=True, userparam=False),
    }

    parameter_overrides = {
            'unit': Override(mandatory=False, default='connected motor(s)'),
            'fmtstr': Override(default='%d', settable=False)
    }

    # Nothing to store in the cache
    _cache_relations = {}

    def create_devices(self):
        """
        This class only supports SinqMotor.

        Create devices that we found to be connected in the _connected_list.
        """
        device_cls_path = 'nicos_sinq.devices.epics.motor.SinqMotor'
        self._build_connected_list()
        for name in self._connected_list:
            # Create motorpv argument from prefix name of connected motor
            # SinqMotor is self configuring
            self._add_device(name, device_cls_path,
                    motorpv=':'.join([self.pvprefix, name]), startdelay=2.0)

    def _get_pv_parameters(self):
        """
        List with each element representing a motor name
        """
        return self.pvsuffixes

    def _get_pv_name(self, pvparam):
        """
        Combine pvprefix and the motor name together with Connected
        suffix to get the PV to check if that specific motor is connected.
        """
        if pvparam in self.pvsuffixes:
            # The convention in SinqMotor is to use Connected suffix
            return ':'.join([self.pvprefix, pvparam, 'Connected'])
        raise ProgrammingError(
                'The motor corresponding to %s is not configured' % pvparam)

    def _build_connected_list(self):
        """
        Create a list of motor suffixes which have connected status.
        """
        # We are not alloved to modify parameter lists, so use a temporary var
        tmp = []
        for pvparam in self._get_pv_parameters():
            device_connected = self._get_pv(pvparam) == 1
            if device_connected:
                tmp.append(pvparam)
        self._connected_list = tmp
        self.read()

    def doRead(self, maxage=0):
        """
        Return the length of the connected list.
        I.e. number of connected motors at startup.
        """
        return len(self._connected_list)

    def doStatus(self, maxage=0):
        return status.OK, ''
