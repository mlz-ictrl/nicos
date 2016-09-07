#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import re

from nicos.core import Param, ConfigurationError, DeviceMixinBase, NicosError


class OptionalLimaFunctionality(object):
    def __init__(self, dev, hwdev):
        self._dev = dev
        self._hwdev = hwdev

        if not self._isFunctionalityAvailable():
            raise NicosError('Functionality not supported')

    def _testFunctionality(self):
        pass

    def _isFunctionalityAvailable(self):
        try:
            self._testFunctionality()
        except NicosError as e:
            if re.match('Error: No .*? capability', e.message):
                return False
            else:
                raise e

        return True


class LimaCooler(DeviceMixinBase):
    parameters = {
        'cooleron': Param('Cooler enabled',
                          type=bool,
                          default=False,
                          volatile=True,
                          settable=True),
    }

    def doReadCooleron(self):
        return True if self._dev.cooler == 'ON' else False

    def doWriteCooleron(self, value):
        self._dev.cooler = 'ON' if value else 'OFF'


class LimaShutter(OptionalLimaFunctionality):
    def __init__(self, dev, hwdev):
        OptionalLimaFunctionality.__init__(self, dev, hwdev)

    def _testFunctionality(self):
        self.doReadShuttermode()

    def doReadShutteropentime(self):
        return self._dev.shutter_open_time

    def doWriteShutteropentime(self, value):
        self._dev.shutter_open_time = value

    def doReadShutterclosetime(self):
        return self._dev.shutter_close_time

    def doWriteShutterclosetime(self, value):
        self._dev.shutter_close_time = value

    def doReadShuttermode(self):
        internalMode = self._dev.shutter_mode

        if internalMode in ['AUTO_FRAME', 'AUTO_SEQUENCE']:
            # this detector is only used in single acq mode,
            # so AUTO_FRAME and AUTO_SEQUENCE have the same
            # behaviour
            return 'auto'
        elif internalMode == 'MANUAL':
            shutterState = self._dev.shutter_manual_state

            if shutterState == 'OPEN':
                return 'always_open'
            elif shutterState == 'CLOSED':
                return 'always_closed'
            else:
                raise ConfigurationError(self, 'Camera shutter has unknown '
                                         + 'state in manual mode (%s)'
                                         % shutterState)
        else:
            raise ConfigurationError(self,
                                     'Camera has unknown shutter mode (%s)'
                                     % internalMode)

    def doWriteShuttermode(self, value):
        if value == 'auto':
            self._dev.shutter_mode = 'AUTO_FRAME'
        elif value == 'always_open':
            self._dev.shutter_mode = 'MANUAL'
            self._dev.openShutterManual()
        elif value == 'always_closed':
            self._dev.shutter_mode = 'MANUAL'
            self._dev.closeShutterManual()
