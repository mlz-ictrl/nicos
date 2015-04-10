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

class Setup(object):
    def __init__(self, info, parent=None):
        self.path = info.keys()[0] + '.py'
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


class Device(object):
    def __init__(self, name, classString='', parameters=None):
        if parameters is None:
            parameters = {}
        self.name = name
        self.classString = classString
        self.parameters = parameters
