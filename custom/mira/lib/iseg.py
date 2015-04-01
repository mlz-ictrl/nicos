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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""MIRA special high voltage power supply device."""

import time

from nicos.core import Param
from nicos.devices.tango import Actuator


class CascadeIsegHV(Actuator):
    """Iseg that warns and waits before switching on the HV."""

    parameters = {
        'waittime': Param('Seconds to wait before ramping up',
                          type=int, settable=True, default=60),
    }

    def doStart(self, value):
        if abs(self.read(0)) < 10 and self.waittime:
            self.log.warning('Please make sure the Cascade detector '
                             'is supplied with counting gas!  Waiting '
                             'for %d seconds before ramping up the HV.'
                             % self.waittime)
            time.sleep(self.waittime)
        return Actuator.doStart(self, value)
