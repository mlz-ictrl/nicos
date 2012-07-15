#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""Detector classes for NICOS."""

__version__ = "$Revision$"

from DetectorClient import DetectorClient

from nicos.tango.frm2device import FRM2Device

from nicos.core import Measurable, Param
from nicos.core.device import usermethod

class Detector(FRM2Device,  Measurable):
    tango_class = DetectorClient

    parameters = {
        'syncmode':  Param('Synchronisation mode', settable=True,
                           type=str, category='general', volatile=True),
        'syncvalue': Param('Synchronisation mode dependend configuration value',
                           settable=True, type=float, category='general',
                           volatile=True),
        'size':      Param('Detector size', settable=False,
                           type=list, category='general', volatile=True),
    }

    def doStart(self):
        self._tango_guard(self._dev.startAcq)

    def doStop(self):
        self._tango_guard(self._dev.stopAcq)

    def doPause(self):
        return False

    def doResume(self):
        return False

    def doReadSyncvalue(self):
        return self._tango_guard(self._dev.syncValue)

    def doReadSyncmode(self):
        return self._tango_guard(self._dev.syncMode)

    def doWriteSyncvalue(self, value):
        self._tango_guard(self._dev.setSyncValue, value)

    def doWriteSyncmode(self, value):
        self._tango_guard(self._dev.setSyncmode, value)

    def doReadSize(self):
        return self._tango_guard(self._dev.detectorSize)

    def doRead(self, maxage=0):
        return self._tango_guard(self._dev.value)

    @usermethod
    def clear(self):
        self._tango_guard(self._dev.clear)
