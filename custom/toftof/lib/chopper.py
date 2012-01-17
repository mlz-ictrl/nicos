#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF chopper calculations and chopper control (MACCON)."""

__version__ = "$Revision$"

import IO

from nicos.core import Moveable, Param, NicosError, intrange
from nicos.taco import TacoDevice

#from nicos.toftof import calculations as calc


class TofChopper(TacoDevice, Moveable):
    taco_class = IO.StringIO

    parameters = {
        'ch5_90deg_offset': Param('Whether chopper 5 is mounted the right way '
                                  '(= 0) or with 90deg offset (= 1)',
                                  type=intrange(0, 2), mandatory=True),
        'phase_accuracy': Param('Required accuracy of the chopper phases',
                                settable=True, default=10), # XXX unit?
        'speed_accuracy': Param('Required accuracy of the chopper speeds',
                                settable=True, default=2),  # XXX unit?
    }

    def _read(self, n):
        return float(self._taco_guard(self._dev.communicate, 'M%04d' % n))

    def _write(self, n, v):
        self._taco_guard(self._dev.write('M%04d=%d' % (n, v)))

    def doInit(self):
        self._phases = [0, 0]
        try:
            if self._mode == 'simulation':
                raise NicosError('not possible in simulation mode')
            self._wavelength = self._read(4181) / 1000.0
            if self._wavelength == 0.0:
                self._wavelength = 4.5   # XXX does this occur?
            slittype = int(self._read(4182))
            if slittype == 2:
                self._slittype = 1
            else:
                self._slittype = 0
            crc = int(self._read(4183))
            if crc == 1:
                self._crc = 0
            else:
                self._crc = 1
            self._speed = round(self._read(4150) / 1118.4735)
            self._ratio = abs(self._read(4507))
            for i in range(2, 8):
                self._phases.append(int(round(self._read(4048 + i*100) / 466.0378)))
        except NicosError:
            self._wavelength = 4.5
            self._speed = 0
            self._ratio = 1
            self._slittype = 0
            self._phases = [0] * 8
            self._crc = 1
            self.log.warning('could not read initial data from PMAC chopper '
                             'controller', exc=1)
        self._waiting = False

    def _is_cal(self):
        for i in range(1, 8):
            ret = int(self._read(4140 + i))
            if ret in [0,1,2,6,8]:
                return False
        return True
