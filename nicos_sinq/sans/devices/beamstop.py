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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos import session
from nicos.core import Attach, Readable, status
from nicos.core.params import Param, oneof
from nicos.devices.abstract import Motor
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod


class SeqLimDev(SeqDev):
    def __init__(self, dev, target, limit):
        SeqDev.__init__(self, dev, target, True)
        self._limit = limit

    def set_limit(self):
        limits = self.dev.userlimits
        self.dev.userlimits = (self._limit, limits[1])

    def check(self):
        self.set_limit()
        return SeqDev.check(self)

    def run(self):
        self.set_limit()
        SeqDev.run(self)


class BeamstopSequencer(BaseSequencer):
    """
    Base class for Beamstop handling classes at SANS
    """

    attached_devices = {
        'x': Attach('Motor for X movement', Motor),
        'y': Attach('Motor for Y movement', Motor),
    }

    parameters = {
        '_in_x': Param('IN x position', type=float, default=0.0,
                       settable=True, internal=True),
        '_in_y': Param('IN y position', type=float, default=0.0,
                       settable=True, internal=True),
    }

    def _fix(self):
        self._attached_x.fix()
        self._attached_y.fix()

    def _release(self):
        self._attached_x.release()
        self._attached_y.release()

    def _save_pos(self):
        self._in_x = self._attached_x.read(0)
        self._in_y = self._attached_y.read(0)


class Beamstop(BeamstopSequencer):
    """
    This is a SANS special device for moving the beamstop in or out. This
    requires a sequence of operations. Order of driving is important.
    """
    _out_x = 28.
    _out_y = -543.
    valuetype = oneof('in', 'out')

    def doRead(self, maxage):
        x = self._attached_x.read(maxage)
        y = self._attached_y.read(maxage)
        summ = abs(x - self._out_x)
        summ += abs(y - self._out_y)
        if summ < 1:
            return 'out'
        return 'in'

    def _generateSequence(self, target):
        seq = []

        s = SeqMethod(self, '_release')
        seq.append(s)

        if target == 'out':
            seq.append(SeqMethod(self, '_save_pos'))

            seq.append(SeqDev(self._attached_x, self._out_x))

            seq.append(SeqLimDev(self._attached_y, self._out_y, self._out_y))

            seq.append(SeqMethod(self, '_fix'))
        else:
            seq.append(SeqMethod(self, '_release'))

            seq.append(SeqLimDev(self._attached_y, self._in_y, -450))

            seq.append(SeqDev(self._attached_x, self._in_x))

        return seq


class BeamstopChanger(BeamstopSequencer):
    """
    A class for changing the beamstop. At SANS this is realised through
    a sequence of motor movements.
    """
    attached_devices = {
        'io': Attach('SPS I/O for reading slot', Readable),
    }

    valuetype = oneof(1, 2, 3, 4)

    _beamstop_pos = {
        1: 28.0,
        2: -100.5,
        3: -220.5,
        4: -340.5,
    }

    def doInit(self, mode):
        # Stopping this procedure can mess up things badly
        self._honor_stop = False

    def _emergencyFix(self, reason):
        session.log.error('%s, Fixing motors, Get a manager to fix this',
                          reason)
        self._fix()

    def doRead(self, maxage):
        dio = self._attached_io.read(maxage)
        test = dio[1]
        val = 1
        count = 0
        for i in range(0, 3):
            if test & 1 << i:
                val = i + 2
                count += 1
        if count > 1:
            self._emergencyFix('Beamstop lost!!!')
        return val

    def doIsAllowed(self, pos):
        if self._attached_y.isAtTarget(-543):
            return False, 'Cannot change beamstop in OUT position'
        return True, ''

    def _testArrival(self, xpos, ypos):
        if not (self._attached_x.isAtTarget(xpos) and
                self._attached_y.isAtTarget(ypos)):
            self._emergencyFix('Beamstop driving failed!!!')

    def _generateSequence(self, target):
        seq = []

        pos = self.read(0)
        self._save_pos()

        xpos = self._beamstop_pos[pos]
        seq.append((SeqDev(self._attached_y, -450),
                    SeqDev(self._attached_x, xpos)))
        seq.append(SeqMethod(self, '_testArrival', xpos, -450.))

        seq.append(SeqLimDev(self._attached_y, -549, -549))
        seq.append(SeqMethod(self, '_testArrival', xpos, -549.))

        xpos = self._beamstop_pos[int(target)]
        seq.append(SeqDev(self._attached_x, xpos))
        seq.append(SeqMethod(self, '_testArrival', xpos,
                             -549.))

        seq.append(SeqLimDev(self._attached_y, -450, -450))
        seq.append(SeqMethod(self, '_testArrival', xpos, -450))

        seq.append((SeqDev(self._attached_y, self._in_y),
                    SeqDev(self._attached_x, self._in_x)))

        return seq

    def _runFailed(self, step, action, exc_info):
        self._emergencyFix('Beamstop motor failed to run!!!')
        BeamstopSequencer._runFailed(self, step, action, exc_info)

    def doStatus(self, maxage=0):
        stat = BaseSequencer.doStatus(self, maxage)
        if stat[0] != status.BUSY and self._seq_is_running():
            return status.BUSY, stat[1]
        return stat
