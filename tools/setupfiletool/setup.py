#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

from copy import copy
from os import path

from nicos.core.sessions.setups import readSetup


class Setup(object):
    def __init__(self, pathToSetup, log, parent=None):
        info = {}
        readSetup(info, pathToSetup, log)

        self.path = pathToSetup
        self.pathNoExtension = info.keys()[0]
        self.description = info[self.pathNoExtension]['description']
        self.group = info[self.pathNoExtension]['group']
        self.includes = copy(info[self.pathNoExtension]['includes'])
        self.excludes = copy(info[self.pathNoExtension]['excludes'])
        self.modules = copy(info[self.pathNoExtension]['modules'])
        self.sysconfig = copy(info[self.pathNoExtension]['sysconfig'])
        self.startupcode = copy(info[self.pathNoExtension]['startupcode'])
        self.devices = []
        devs = info[self.pathNoExtension]['devices']
        for deviceName in devs:
            self.devices.append(Device(deviceName,
                                       devs[deviceName][0],
                                       copy(devs[deviceName][1])))

    @staticmethod
    def getDeviceNamesOfSetup(pathToSetup, log):
        # returns the names of devices of a setup
        info = {}
        readSetup(info, pathToSetup, log)
        modname = path.basename(path.splitext(pathToSetup)[0])
        devices = []
        if modname in info and 'devices' in info[modname]:
            for device in info[modname]['devices'].keys():
                devices.append(device)
        return devices

    @staticmethod
    def getDeviceOfSetup(pathToSetup, deviceName, log):
        # returns a Device instance of a setup identified by the name.
        setup = Setup(pathToSetup, log)
        for device in setup.devices:
            if device.name == deviceName:
                return device
        # if no device with the corresponding name was found in the setup,
        # create a new one.
        return Device(deviceName)


class Device(object):
    def __init__(self, name, classString='', parameters=None):
        if parameters is None:
            parameters = {}
        self.name = name
        self.classString = classString
        self.parameters = parameters
