# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

from nicos.core import Moveable, Param, oneof
from nicos.core.params import Attach
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class MorpheusSpin(BaseSequencer):

    attached_devices = {
        'magnet_c': Attach('Magnet-C', Moveable),
        'magnet_f': Attach('Magnet-F', Moveable),
    }

    parameters = {
        'su_c': Param('Spin-up value for Magnet-C', type=float,
                      mandatory=True, settable=True, userparam=True),
        'su_f': Param('Spin-up value for Magnet-F',
                      type=float, mandatory=True, settable=True,
                      userparam=True),
    }

    valuetype = oneof(0, 1, '+', '-', 'up', 'down')

    def _generateSequence(self, target):
        seq = []

        if target in [0, '+', 'up']:
            seq.append((SeqDev(self._attached_magnet_c, self.su_c)))
            seq.append(SeqSleep(1.))
            seq.append(SeqDev(self._attached_magnet_f, self.su_f))
        elif target in [1, '-', 'down']:
            seq.append((SeqDev(self._attached_magnet_c, 0.)))
            seq.append(SeqSleep(1.))
            seq.append(SeqDev(self._attached_magnet_f, 0.))

        return seq

    def doRead(self, maxage=0):
        if self._attached_magnet_c.isAtTarget(target=self.su_c) and \
           self._attached_magnet_f.isAtTarget(target=self.su_f):
            return 0
        if self._attached_magnet_c.isAtTarget(target=0.) and \
           self._attached_magnet_f.isAtTarget(target=0.):
            return 1
        return -1
