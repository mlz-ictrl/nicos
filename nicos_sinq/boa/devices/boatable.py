#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

"""
Implementation of BOA tables. BOA has 4 different stations, called tables,
onto which various pieces of equipment can be attached. The configuration of
these tables influences the layout of the data file. Users and scripts need
to be able to view and modify the tables.
"""

import itertools

from nicos import session
from nicos.core import Device, Param, listof, nicosdev, usermethod


class BoaTable(Device):
    parameters = {
        'standard_devices': Param('Standard Devices', type=listof(nicosdev),
                                  userparam=False),
        'setups': Param('setups on this table', type=listof(str),
                        userparam=False, settable=True, default=[]),
        'additional_devices': Param('additional devices attached '
                                    'to the table', type=listof(nicosdev),
                                    default=[], settable=True,
                                    userparam=False), }

    def doInit(self, mode):
        self.hardware_access = False

    @usermethod
    def addSetup(self, name):
        if name not in session.loaded_setups:
            raise ValueError('%s not a loaded setup' % name)
        if name not in self.setups:
            tmp = list(self.setups)
            tmp.append(name)
            self.setups = tmp

    @usermethod
    def removeSetup(self, name):
        if name in self.setups:
            tmp = list(self.setups)
            tmp.remove(name)
            self.setups = tmp

    @usermethod
    def addDevice(self, name):
        if name not in session.configured_devices:
            raise ValueError('device %s is not available' % name)
        if name not in self.additional_devices:
            tmp = list(self.additional_devices)
            tmp.append(name)
            self.additional_devices = tmp

    @usermethod
    def removeDevice(self, name):
        if name in self.additional_devices:
            tmp = list(self.additional_devices)
            tmp.remove(name)
            self.additional_devices = tmp

    @usermethod
    def show(self):
        txt = 'Table %s Configuration:\n' % self.doReadName()
        txt += 'Standard Devices:\n'
        txt += '\t %s\n' % ', '.join(self.standard_devices)
        txt += 'Setups:\n'
        txt += '\t%s\n' % ', '.join(self.setups)
        txt += 'Additional Devices\n'
        txt += '\t%s\n' % ', '.join(self.additional_devices)
        txt += 'Total Devices\n'
        txt += '\t%s\n' % ', '.join(self.getTableDevices())
        session.log.info(txt)

    def getTableDevices(self):
        result = list(
            itertools.chain(self.standard_devices, self.additional_devices))
        setupInfo = session.getSetupInfo()
        for setup in self.setups:
            info = setupInfo[setup]
            result = list(itertools.chain(result, info['devices'].keys()))
        return result
