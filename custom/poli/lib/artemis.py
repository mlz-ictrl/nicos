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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Stub detector for neutron camera.  Waits until a new file is added."""

import os
import time

from nicos.core import Param, Measurable, TimeoutError, Value, status


class ArtemisCapture(Measurable):

    parameters = {
        'datapath': Param('Path to watch for new files', mandatory=True,
                          type=str),
    }

    def doInit(self, mode):
        self._existing = set(os.listdir(self.datapath))
        self._lastfile = ''
        self._timeout = 10
        self._started = 0

    def doRead(self, maxage=0):
        return [self._lastfile]

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def valueInfo(self):
        return Value(self.name + '.file', type='filename', fmtstr='%s'),

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._timeout = preset['t']

    def doStart(self):
        self.log.debug('camera doStart')
        self._existing = set(os.listdir(self.datapath))
        self._lastfile = ''
        self._started = time.time()

    def doFinish(self):
        self.log.debug('camera doFinish')
        self._started = 0

    def doStop(self):
        self.doFinish()

    def doIsCompleted(self):
        if self._started == 0:
            return True
        # self.log.debug('camera doIsCompleted')
        newset = set(os.listdir(self.datapath))
        diff = newset - self._existing
        if diff:
            if len(diff) > 1:
                self.log.warning('more than one new file found!')
            self._existing = newset
            self._lastfile = diff.pop()
            self._started = 0
            return True
        if self._started + self._timeout < time.time():
            self._started = 0
            raise TimeoutError(self, 'no new image appeared within %d sec' %
                               self._timeout)
        return False
