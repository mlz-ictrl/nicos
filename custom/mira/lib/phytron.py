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

"""MIRA specific axis classes."""

import time

import IO
import Motor

from nicos.core import CommunicationError
from nicos.devices.taco.axis import Axis as TacoAxis


class Axis(TacoAxis):
    """
    A Phytron specific axis -- on doReset() it tries to reset the Phytron
    controller as well as the TACO server.
    """

    def _reset_phytron(self):
        motor = Motor.Motor(self._taco_guard(self._dev.deviceQueryResource, 'motor'))
        iodev = self._taco_guard(motor.deviceQueryResource, 'iodev')
        addr = self._taco_guard(motor.deviceQueryResource, 'address')
        client = IO.StringIO(iodev)
        self.log.info('Resetting Phytron controller...')
        # save all parameters prior to reset (doesn't reply)
        self._taco_guard(client.writeLine, '\x02%sSA' % addr)
        # which takes quite a lot of time
        time.sleep(0.5)
        for _i in range(10):
            try:
                self._taco_guard(client.communicate, '\x02%sIVR' % addr)
                break
            except CommunicationError:
                time.sleep(0.5)
        else:
            raise CommunicationError(self, 'controller not responding after '
                                     'parameter save')
        # do the controller reset
        self._taco_guard(client.communicate, '\x02%sCR' % addr)
        time.sleep(0.2)
        self.log.info('Phytron reset complete')

    def doReset(self):
        TacoAxis.doReset(self)
        self._reset_phytron()
