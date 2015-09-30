#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Christian Randau <christian.randau@frm2.tum.de>
#
# *****************************************************************************

"""UniversalDeviceClient (UDC) to access devices provided by Corba servers such
as CARESS or UniversalDeviceProxy.
"""

import UniversalDeviceClient as UDC  # pylint: disable=import-error

from nicos.core import Moveable, Readable, Param, Override, HasPrecision, \
    HasLimits, status, ProgrammingError


class UDCReadable(Readable):
    """Abstract class for UDC Readable (Interface).

    Please create no objects from this class, to create an object please use a
    child class, e.g. UDCReadableDevice.  Please note everything inherited from
    this class is readonly.
    """

    parameter_overrides = {
        'pollinterval': Override(default = 1),
        'maxage':       Override(default = 1.1),
    }

    parameters = {
        'dev_type': Param('The device type as a string, '
                          'e.g. CARESS_HWB, CARESS_GENERICDEVICE, DOLI, '
                          'MODBUS_EUROTHERM_2400, '
                          'MODBUS_EUROTHERM_2400_OUTPUTLEVEL, '
                          'MODBUS_EUROTHERM_3500, '
                          'MODBUS_EUROTHERM_3500_OUTPUTLEVEL',
                          type=str, mandatory=True, userparam=False),
    }

    def _initPrivateMember(self):
        # Init local members
        self._last_value = 0
        self._last_status = status.UNKNOWN
        self._last_status_txt = 'UNKNOWN'

        self._numberOfStatusRequestsBeforeReinit = 5
        self._counterOfUnconnectedStatusRequests = 0

        # Set Debug level of IDC
        # ToDo
        UDC.UDebug_setDebugLevel(UDC.UDebug.UDebugLevel_Info)

    def _checkIsCaress(self):
        return self.dev_type in ("CARESS_GENERICDEVICE", "CARESS_HWB")

    def _validateDevType(self):
        # ToDo check all elements of the device parameter list
        self.log.info("Attention: _validateDevType is not implemented!")
        return True

    def _setPrecisionAndRanges(self):
        self.log.debug("Attention: A readable has no precision or ranges!")

    def doPreinit(self, mode):
        raise ProgrammingError("It is not allowed to create an instance of "
                               "this abstract class!")

    def doInit(self, mode):
        if mode == 'simulation':
            self.log.debug("Init in simulation mode: release the connection")
            self._device.release()
            return
        self.log.debug("Set internal polling interval to %d ms" %
                       (int(self.pollinterval) * 500))
        self._device.setPollingIntervalTime_ms(int(self.pollinterval) * 500)
        self.log.debug("Init no simulation mode: connect to device")

        # Connect to CORBA Srv
        self._counterOfUnconnectedStatusRequests = 0
        self._device.init()
        if mode == 'master':
            self._setPrecisionAndRanges()

    def doShutdown(self):
        self.log.debug("shutdown: release the connection to device")
        self._device.release()

    def doVersion(self):
        return UDC.getVersion_UDC()

    def doRead(self, maxage=0):
        if self._device.getIsConnected():
            self._last_value = self._device.getValue()

        return self._last_value

    def doStatus(self, maxage=0):
        if self._device.getIsConnected():
            devstatus = self._device.getStatus()
            self.log.debug('status: %s' % devstatus)
            if devstatus == UDC.status_done:
                return status.OK, 'done'
            elif devstatus == UDC.status_run:
                return status.BUSY, 'moving'
            elif devstatus == UDC.status_error:
                return status.ERROR, 'error'
            elif devstatus == UDC.status_wait:
                return status.BUSY, 'wait'
            return status.UNKNOWN, str(devstatus)
        else:
            # Try to reconnect
            self._counterOfUnconnectedStatusRequests += 1
            if self._counterOfUnconnectedStatusRequests \
               > self._numberOfStatusRequestsBeforeReinit:
                self.log.debug("Init: Try connect to the device again")
                self.doReset()
            return status.ERROR, 'device disconnected'

    def doReset(self):
        self.doShutdown()
        self.doInit(self._mode)


class UDCWriteable(HasLimits, HasPrecision, UDCReadable, Moveable):
    """Abstract class for UDC Writeable (Interface).

    Please create no objects from this class, to create an object please use a
    child class e.g. UDCWriteableDevice.  Please note everything inherited from
    this class has the right to write. It is not allowed to create more than one
    writable client for one real device.

    Attention:
    It is not forbidden to create more than one client, but it can fail.
    """
    def _setPrecisionAndRanges(self):
        self.log.debug("set Ranges: min=%s max=%s" % self.abslimits)
        self._device.setRanges(*self.abslimits)
        self.log.debug("set Tolerance: precision=%s" % self.precision)
        self._device.setToleranz(self.precision)

    # Functions from Moveable
    def doStart(self, pos):
        self.log.debug("Start movement: target=%s" % pos)
        self._device.setTargetValue(pos)
        self._device.start()
        self._device.waitToCmdExecuted()

    def doStop(self):
        self.log.debug("Stop movement")
        self._device.stop()
        self._device.waitToCmdExecuted()


class UDCReadableDevice(UDCReadable):
    """Full implemented Readable class for standard devices.

    Please create for read only use of your device an object from this class.
    """
    parameters = {
        'path':   Param('The path string of the init-file for this device.',
                        type=str, mandatory=True, userparam=False),
    }

    def doPreinit(self, mode):
        self._initPrivateMember()

        if not self._validateDevType():
            raise ProgrammingError(self, "The given dev_type is wrong")

        if self._checkIsCaress():
            raise ProgrammingError(self, "Use UDCReadableCaressDevice "
                                   "to create an instance with the type %s"
                                   % self.dev_type)

        self.log.debug("Create UDevice from the dev_type %s" % self.dev_type)
        self._device = UDC.UDevice(self.dev_type)
        self._device.setSettingsFilePath(self.path)


class UDCWriteableDevice(UDCReadableDevice, UDCWriteable):
    """Full implemented Writeable class for standard devices.

    Please create for writable use of your device an object from this class. It
    is not allowed to create more than one writable client for one real device.

    Attention:
    It is not forbidden to create more than one client, but it can fail.
    """
    def doPreinit(self, mode):
        self._initPrivateMember()

        if not self._validateDevType():
            raise ProgrammingError(self, "The given dev_type is wrong")

        if self._checkIsCaress():
            raise ProgrammingError(self, "Use UDCWriteableCaressDevice "
                                   "to create an instance with the type %s"
                                   % self.dev_type)

        self.log.debug("Create UDeviceControllable from the dev_type %s"
                       % self.dev_type)
        self._device = UDC.UDeviceControllable(self.dev_type)
        self._device.setSettingsFilePath(self.path)


class UDCReadableCaressDevice(UDCReadable):
    """Special Readable child class for CARESS devices.

    Please create for read only use of CARESS devices an object from this class.
    """
    parameters = {
        'corba_server_name': Param('The name of the CORBA-Server '
                                   'as a string for this device',
                                   type=str, mandatory=True, userparam=False),
        'corba_device_name': Param('The name of the device as a string.',
                                   type=str, mandatory=True, userparam=False),
        'corba_init_line':   Param('The parameter line from the Hardware_'
                                   'Modules.dat as a string for this device.',
                                   type=str, mandatory=True, userparam=False),
    }

    def _setDeviceCaressParameter(self, device, mode):
        self.log.debug("Set CORBA_Server_Name=" + self.corba_server_name)
        device.setCorbaServerName(self.corba_server_name)
        self.log.debug("Set CORBA_Device_Name=" + self.corba_device_name)
        device.setCorbaDeviceName(self.corba_device_name)
        self.log.debug("Set CORBA_Init_Line=" + self.corba_init_line)
        device.setCorbaInitParameterLine(self.corba_init_line)
        device.setName(self.name)
        if mode == 'master':
            self.log.debug("Set CorbaInitOption=master")
            device.setCorbaInitOption(UDC.caressInitOption_master)
        elif mode == 'slave':
            self.log.debug("Set CorbaInitOption=slave")
            device.setCorbaInitOption(UDC.caressInitOption_slave)
        elif mode == 'maintenance':
            self.log.debug("Set CorbaInitOption=master")
            device.setCorbaInitOption(UDC.caressInitOption_master)
        else:
            self.log.debug("Set CorbaInitOption=slave")
            device.setCorbaInitOption(UDC.caressInitOption_slave)

    def doPreinit(self, mode):
        self._initPrivateMember()

        if not self._validateDevType():
            raise ProgrammingError(self, "The given dev_type is wrong")

        if not self._checkIsCaress():
            raise ProgrammingError(self, "Use UDCReadableDevice "
                                   "to create an instance with the type %s"
                                   % self.dev_type)

        # Create the instance of the device
        self.log.debug("Create UDevice from the dev_type %s" % self.dev_type)
        self._device = UDC.UDevice(self.dev_type)

        # Create a casted instance of the device.
        # Attention this is only reference copy and no new device.
        self.log.debug("Cast UDevice to UDeviceCaress!")
        deviceTemp = UDC.UDeviceCaress(self._device)
        self._setDeviceCaressParameter(deviceTemp, mode)


class UDCWriteableCaressDevice(UDCReadableCaressDevice, UDCWriteable):
    """Special Writeable child class for CARESS devices.

    Please create for writable use of CARESS devices an object from this class.
    It is not allowed to create more than one writable client for one real
    device.

    Attention:
    It is not forbidden to create more than one client, but it can fail.

    Info: For a correct status handling it is necessary to create readOnly
    devices for slaves. ReadOnly (UDevice) devices get the current status
    information directly from the caress server.
    Writable (UDeviceControllable) devices have their own state machine.
    Hence, they don't get the original status from the server.
    """
    def doPreinit(self, mode):
        self._initPrivateMember()

        if not self._validateDevType():
            raise ProgrammingError(self, "The given dev_type is wrong")

        if not self._checkIsCaress():
            raise ProgrammingError(self, "Use UDCWriteableDevice "
                                   "to create an instance with the type %s"
                                   % self.dev_type)

        if mode == 'slave':
            # Create the instance of the device
            self.log.debug("Create UDevice from the dev_type %s" %
                           self.dev_type)
            self._device = UDC.UDevice(self.dev_type)
            # Create a casted instance of the device.
            # Attention this is only reference copy and no new device.
            self.log.debug("Cast UDevice to UDeviceCaress!")
            deviceTemp = UDC.UDeviceCaress(self._device)
            self._setDeviceCaressParameter(deviceTemp, mode)
        else:
            # Create the instance of the device
            self.log.debug("Create UDeviceControllable from the dev_type %s" %
                           self.dev_type)
            self._device = UDC.UDeviceControllable(self.dev_type)
            # Create a casted instance of the device.
            # Attention this is only reference copy and no new device.
            self.log.debug("Cast UDeviceControllable "
                           "to UDeviceControllableCaress!")
            deviceTemp = UDC.UDeviceControllableCaress(self._device)
            self._setDeviceCaressParameter(deviceTemp, mode)
