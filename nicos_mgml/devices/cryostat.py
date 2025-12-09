# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""MGML cryostat device for Helium consumption monitoring."""

from math import isnan
from time import time

from numpy import array, interp

from nicos import session
from nicos.commands.output import printinfo
from nicos.core import Attach, Param, Readable, status
from nicos.core.params import listof, none_or, tupleof
from nicos.core.utils import usermethod


class Cryostat(Readable):

    parameters = {
        'consumedhelium': Param('Consumed helium in litres',
                                type=float, userparam=False, internal=True),
        'filledby':       Param('User who did last filling',
                                type=str, internal=True, userparam=True),
        'lastfilled':     Param('The amount of helium consumed for last filling',
                                type=float, userparam=False, internal=True),
        'lastcoeff':      Param('Coefficiant of helium losses from the last fill',
                                type=float, userparam=False, internal=True,
                                default=1.),
        'calibration':    Param('Calibration of cryostat volume',
                                type=listof(tupleof(float, float)),
                                settable=False),
        'fillstart':      Param('When the filling of cryo started (sec since '
                                'epoch), none if not filling.',
                                type=none_or(float), userparam=False,
                                internal=True, default=None),
    }

    attached_devices = {
        'levelmeter': Attach('Where to get the helium level', Readable,
                             optional=True),
        'gasmeter': Attach('Where to get the used gas amount', Readable,
                           optional=True),
    }

    _levelmeter_start = 0
    _gasmeter_start = 0
    _levelmeter_end = 0
    _gasmeter_end = 0

    #
    #  convert level to litres
    #
    def _level2l(self, level=None):
        if not level:
            level = self._attached_levelmeter.read(0)
        return interp(level, *array(self.calibration).T)

    @usermethod
    def StartFill(self):
        if self.fillstart:
            self.log.warning('Filling is already started.')
            return
        self._levelmeter_start = self._attached_levelmeter.read(0)
        self._gasmeter_start = self._attached_gasmeter.read(0)
        self._setROParam('fillstart', time())
        printinfo(f'[Cryostat] Filling started: LHe: {self._levelmeter_start} %, '
                  f'Gas: {self._gasmeter_start}')
        if session.experiment._addConsumedHelium:
            session.experiment._addConsumedHelium()

    @usermethod
    def EndFill(self, consumed, filledby):
        if not self.fillstart:
            self.log.error('You need to start filling first.')
            return
        if consumed < 0:
            self.log.error('You need to enter positive amount of litres consumed')
            return
        self._levelmeter_end = self._attached_levelmeter.read(0)
        self._gasmeter_end = self._attached_gasmeter.read(0)
        printinfo(f'[Cryostat] Filling ended: LHe: {self._levelmeter_end} %, '
                  f'Gas: {self._gasmeter_end}')
        filledlitres = self._level2l(self._levelmeter_end) - self._level2l(self._levelmeter_start)
        if isnan(self.lastcoeff):
            self.log.info('Last cryostat coefficient was NaN. Fixing lastcoeff to 1.')
            self._setROParam('lastcoeff', 1)
        filledlitres = max(filledlitres, 0)
        if filledlitres > 0:
            self._setROParam('lastcoeff', consumed / filledlitres)
            printinfo(f'[Cryostat] Consumed {consumed} l, that is {self.lastcoeff:.2f}x '
                      f'more than filled-in ({filledlitres}l).')
        else:
            printinfo('[Cryostat] Cryostat coefficient not changed since LHe '
                      'level did not increased!')
        self._setROParam('lastfilled', consumed)
        self._setROParam('filledby', filledby)
        self._setROParam('consumedhelium', self.consumedhelium + consumed)
        self._setROParam('fillstart', None)
        if session.experiment._setStartLevel:
            session.experiment._setStartLevel()

    def doRead(self, maxage=0):
        return self._attached_levelmeter.read(maxage)

    def doStatus(self, maxage=0):
        if self.fillstart:
            return status.BUSY, f'Filling helium ({time() - self.fillstart:.0f} s)'
        return status.OK, ''


class DummyCryostat(Cryostat):

    def _level2l(self, level=None):
        return 0

    @usermethod
    def StartFill(self):
        pass

    @usermethod
    def EndFill(self, consumed, filledby):
        pass

    def doRead(self, maxage=0):
        return 0

    def doStatus(self, maxage=0):
        return status.OK, ''
