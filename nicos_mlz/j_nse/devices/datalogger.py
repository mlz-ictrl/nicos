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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import time

from nicos.core import Override, Readable
from nicos.devices.tango import PyTangoDevice


class LastEvent(PyTangoDevice, Readable):
    valuetype = str

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doReadUnit(self):
        return ''

    def doRead(self, maxage=0):
        # The PLC stores the timestamp of the last event as two float values,
        # for example 24/06/2018 12:13:14 is [180624.0, 121314.0].
        date, tod = map(int, self._dev.value)
        year = date // 10000
        month = (date % 10000) // 100
        day = date % 100
        hour = tod // 10000
        minute = (tod % 10000) // 100
        second = tod % 100
        # add +1 hour for timezone
        ts = time.mktime((year, month, day, hour+1, minute, second, 0, 0, 0))
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
