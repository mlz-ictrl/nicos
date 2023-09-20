#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
import math

from nicos.core import IsController
from nicos.core.device import Moveable, Readable
from nicos.core.errors import LimitError, PositionError
from nicos.core.params import Attach, Param
from nicos.devices.generic.sequence import SeqDev, SeqMethod, SequencerMixin


class NODirector(IsController, SequencerMixin, Readable):
    """
    This is for a neutron optics device which moves on flexors
    in two directions. The flexors can only deal with a limited
    movement difference. Two movements, tilt and translation are
    possible. This device makes sure that the flexor limits are
    not exceeded. It translates the tilt angle into the translations
    movements required to set the tilt angle. As we do not have
    synchronisation in the motor controller, movements are carried
    out stepwise in steps which make sure that the flexor limits
    are not exceeded.
    """
    attached_devices = {
        'm1': Attach('First coupled motor', Moveable),
        'm2': Attach('Second coupled motor', Moveable),
    }

    parameters = {
        'maxdiv': Param('Maximum allowed difference between m1, m2',
                        type=float),
        'm1_length': Param('Distance to first motor', type=float),
        'm2_length': Param('Distance to the second motor', type=float),
        'position': Param('Position of the NO device', type=float,
                          settable=True, userparam=True, volatile=True),
        'tilt': Param('Tilt of the NO device', type=float,
                      settable=True, userparam=True, volatile=True),
    }

    def doInit(self, mode):
        self._ignore_maxdiv = False
        self._target = None

    def _calculateTargets(self, position, tilt):
        m1 = m2 = position
        m1 += self.m1_length * math.tan(math.radians(tilt))
        m2 += self.m2_length * math.tan(math.radians(tilt))
        return m1, m2

    def _generateSequence(self):
        seq = []

        cur_m1 = self._attached_m1.read(0)
        cur_m2 = self._attached_m2.read(0)
        step_size = self.maxdiv/2.
        m1_step = abs(cur_m1 - self._target[0])/step_size
        m2_step = abs(cur_m2 - self._target[1])/step_size
        nsteps = int(math.floor(max(m1_step, m2_step)))

        sign = 1 if self._target[0] > cur_m1 else -1
        step_size = abs(cur_m1 - self._target[0])/max(nsteps, 1)
        m1_steps = [(cur_m1 + s * sign * step_size) for s in range(nsteps)]
        m1_steps.append(self._target[0])

        sign = 1 if self._target[1] > cur_m1 else -1
        step_size = abs(cur_m2 - self._target[1]) / max(nsteps, 1)
        m2_steps = [(cur_m2 + s * sign * step_size) for s in range(nsteps)]
        m2_steps.append(self._target[1])

        for t1, t2 in zip(m1_steps, m2_steps):
            seq.append((SeqDev(self._attached_m1, t1),
                        SeqDev(self._attached_m2, t2)))
            seq.append(SeqMethod(self, '_testArrival', t1, t2))

        return seq

    def _testArrival(self, xpos, ypos):
        if not (self._attached_m1.isAtTarget(xpos) and
                self._attached_m2.isAtTarget(ypos)):
            raise PositionError('Motors did not reach %f, %f' % (xpos, ypos))

    def _startMotors(self, m1, m2):
        if abs(m1 - m2) > self.maxdiv:
            raise LimitError('Difference between m1, m2 to large')
        self._ignore_maxdiv = True
        self._target = (m1, m2)
        SequencerMixin.doReset(self)
        self._startSequence(self._generateSequence())

    def doWritePosition(self, position):
        m1, m2 = self._calculateTargets(position, self.tilt)
        self._startMotors(m1, m2)

    def doWriteTilt(self, tilt):
        m1, m2 = self._calculateTargets(self.position, tilt)
        self._startMotors(m1, m2)

    def doStatus(self, maxage=0):
        st, msg = SequencerMixin.doStatus(self, maxage)
        if st not in self.busystates:
            self._ignore_maxdiv = False
        return st, msg

    def isAdevTargetAllowed(self, adev, adevtarget):
        if self._ignore_maxdiv:
            return True, ''
        if adev == self._attached_m1:
            othertarget = self._attached_m2.target
        else:
            othertarget = self._attached_m1.target
        if abs(othertarget - adevtarget) > self.maxdiv:
            return False, 'Motor target difference for %s to large' % adev.name
        return True, ''

    def doReadTilt(self):
        m1 = self._attached_m1.read(0)
        m2 = self._attached_m2.read(0)
        delta_val = m2 - m1
        delta_diff = self.m2_length - self.m1_length
        dt = delta_val / delta_diff
        return math.degrees(math.atan(dt))

    def doReadPosition(self):
        m1 = self._attached_m1.read(0)
        tilt_diff = self.m1_length * math.tan(math.radians(self.tilt))
        return m1 - tilt_diff

    def doRead(self, maxage=0):
        # make the poller happy
        pass

    def doStop(self):
        SequencerMixin.doStop(self)
