#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""Classes for the focussing guide."""

import time

from nicos.core import Attach, Moveable, Param, status
from nicos.utils import createThread


class BeamFocus(Moveable):

    attached_devices = {
        'ellipse': Attach('output signal for ellipse', Moveable),
        'collimator': Attach('output signal for collimator', Moveable)
    }

    parameters = {
        'timeout': Param('sleeping time after moving',
                         type=float, settable=False, default=8),
    }

    def doInit(self, mode):
        self._timer = True
        self._thread = None
        ell_state = self._attached_ellipse.read()
        col_state = self._attached_collimator.read()

        if [ell_state, col_state] == [1, 1]:
            # reset
            self._reset()

    def _reset(self):
        self._attached_ellipse.move(0)
        self._attached_collimator.move(0)

    def doIsAllowed(self, pos):
        if self.doStatus()[0] == status.BUSY:
            return False, 'Device Busy'
        if pos in ['Ell', 'Col']:
            return True, 'Ok'
        return False, 'Invalid Value'

    def doStart(self, pos):
        if pos == self.doRead():
            return
        if pos == 'Ell':
            self._attached_collimator.move(0)
            self._attached_ellipse.move(1)
        elif pos == 'Col':
            self._attached_ellipse.move(0)
            self._attached_collimator.move(1)
        self._timer = False
        self._thread = createThread('sleep', self._wait)

    def doStatus(self, maxage=0):
        # poller gives wrong state but maw works
        if self._timer is False:
            return status.BUSY, 'moving/waiting'
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        ell = self._attached_ellipse.read(maxage)
        col = self._attached_collimator.read(maxage)
        # if self._timer == False:
        #    return None
        if [ell, col] == [0, 1]:
            return 'Col'
        elif [ell, col] == [1, 0]:
            return 'Ell'
        else:
            return None

    def _wait(self):
        time.sleep(self.timeout)
        self._timer = True
