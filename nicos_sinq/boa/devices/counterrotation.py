#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""Implementation of BOA counter rotating motors. BOA often has two rotation
tables installed on  a given component position, each with different bits
attached to it. Now the requirement is to move one of those motors, thereby
leaving the other pointing in the same direction:.i.e the second rotation
has to be moved in the other direction as the first motor by the same
amount. Doing this perfectly would require synchronisation in the motor
controller electronics. But the experience shows that doing this from the
top level is good enough. It helps that the participating motors are of the
same type and have the same speed."""

from nicos.core import Attach, Param
from nicos.core.device import Moveable
from nicos.core.utils import multiStop


class CounterRotatingMotor(Moveable):
    attached_devices = {
        'master': Attach('Master Motor', Moveable),
        'slave': Attach('Slave Motor', Moveable)}

    parameters = {
        'slave_offset': Param('offset of master against slave',
                              type=float,
                              settable=True,
                              userparam=False,
                              prefercache=True,
                              internal=True),
        'old_target': Param('the last known target value',
                            type=float,
                            settable=True,
                            userparam=False,
                            prefercache=True,
                            internal=True), }

    def doInit(self, mode):
        self._offset = self._attached_master.read(0)\
                       - self._attached_slave.read(0) - 2. * self.old_target

    def _calcNewPos(self, pos):
        """"
         Motors can be moved individually, therefore recalculate
         the offset. What we want is that the motors move by the
         same amount in opposite directions to each other. Errors
         moving the motors go into the offset and are corrected by the
         instrument use rby moving motors individually.
        """
        master_pos = self._attached_master.read(0)
        slave_pos = self._attached_slave.read(0)
        self.slave_offset = master_pos - slave_pos - 2. * self.old_target
        diff = pos - self.old_target
        master_pos = master_pos + diff
        slave_pos = slave_pos - diff
        return master_pos, slave_pos

    def doIsAllowed(self, pos):
        master_pos, slave_pos = self._calcNewPos(pos)
        ok, why = self._attached_master.isAllowed(master_pos)
        if not ok:
            return False, '%d violates limit of master motor: %s' % (pos, why)
        ok, why = self._attached_slave.isAllowed(slave_pos)
        if not ok:
            return False, '%d violates limit of slave motor: %s' % (pos, why)
        return True, ''

    def doStart(self, target):
        master_pos, slave_pos = self._calcNewPos(target)
        self._attached_master.start(master_pos)
        self._attached_slave.start(slave_pos)
        self.old_target = target

    def doRead(self, maxage=0):
        return ((self._attached_master.read(0)
                 - self.slave_offset) - self._attached_slave.read(0)) / 2.

    def doStop(self):
        multiStop(self._adevs)
