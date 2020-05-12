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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************
from contextlib import contextmanager
from math import asin, degrees, fabs, radians, sin, tan

from nicos.core import Attach, HasLimits, IsController, Moveable, Param
from nicos.core.errors import NicosError, PositionError
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqMethod


class DoubleMonochromator(HasLimits, IsController, BaseSequencer):
    """
    This class represents a double crystal monochromator as used at PSI.
    The two blades of the monochromator cannot safely pass each other.Thus
    a sequence is needed where the blades are moved into a safe position, then
    the translation is moved and then the blades are moved to the correct two
    theta.
    """

    attached_devices = {
        'mth1': Attach('First monochromator blade theta', Moveable),
        'mth2': Attach('Second monochromator blade theta', Moveable),
        'mtx': Attach('Translation between blades', Moveable), }

    parameters = {
        'safe_position': Param('Position at which the blades can pass each '
                               'other safely', type=float),
        'dvalue': Param('Lattice constant of Monochromator blades', type=float,
                        mandatory=True),
        'distance': Param('Parallactic distance of monos', type=float,
                          mandatory=True), }
    _allowed_called = False

    @contextmanager
    def _allowed(self):
        """Indicator: position checks will done by controller itself.

        If the controller methods ``doStart`` or ``doIsAllowed`` are called the
        ``isAdevTargetAllowed`` must give back always True otherwise a no
        movement of any component can be achieved.
        """
        self._allowed_called = True
        yield
        self._allowed_called = False

    def _checksafe(self):
        if fabs(self._attached_mth1.read(
                0) - self.safe_position) > self._attached_mth1.precision:
            raise NicosError(self, 'MTH1 has not reached a safe position')
        if fabs(self._attached_mth2.read(
                0) - self.safe_position) > self._attached_mth2.precision:
            raise NicosError(self, 'MTH2 has not reached a safe position')

    def _calcMonoPosition(self, target):
        theta = degrees(asin(target / float(2 * self.dvalue)))
        trans = self.distance / tan(2 * radians(theta))
        return theta, trans

    def _checkArrival(self):
        theta, trans = self._calcMonoPosition(self.target)
        th1 = self._attached_mth1.read(0)
        th2 = self._attached_mth2.read(0)
        if abs(th1 - th2) > self._attached_mth1.precision:
            raise PositionError('Double Monochromator blades out of sync, '
                                '%f versus %d' % (th1, th2))
        if abs(th1 - theta) > self._attached_mth1.precision:
            raise PositionError('Blades did not arrive at target')

        if (abs(trans - self._attached_mtx.read(
                0))) > self._attached_mtx.precision:
            raise PositionError('Double monochromator translation not in '
                                'position, should %f, is %f'
                                % (trans, self._attached_mtx.read(0)))

    def _runMtx(self, trans):
        with self._allowed():
            self._attached_mtx.maw(trans)

    def _generateSequence(self, target):
        theta, trans = self._calcMonoPosition(target)

        seq = []

        seq.append((SeqDev(self._attached_mth1, self.safe_position),
                    SeqDev(self._attached_mth2, self.safe_position)))

        seq.append(SeqMethod(self, '_checksafe'))

        seq.append(SeqMethod(self, '_runMtx', trans))

        seq.append((SeqDev(self._attached_mth1, theta),
                    SeqDev(self._attached_mth2, theta)))

        seq.append(SeqMethod(self, '_checkArrival'))

        return seq

    def doRead(self, maxage=0):
        theta = self._attached_mth1.read(maxage)
        return abs(2 * self.dvalue * sin(radians(theta)))

    def isAdevTargetAllowed(self, adev, adevtarget):
        if self._allowed_called:
            return True, ''

        if adev == self._attached_mtx:
            test = self._checksafe()
            if test:
                return True, 'Position Allowed'
            else:
                return False, 'Monochromator blades not in a safe position'
        else:
            return True, 'Position Allowed'
