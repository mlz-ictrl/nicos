#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual chopper devices for testing."""

from time import time as currenttime

from nicos import session
from nicos.core import ADMIN, Attach, NicosError, Override, Param, POLLER, \
    SIMULATION, floatrange, requires, status

from nicos.devices.generic.virtual import VirtualMotor
from nicos.pycompat import xrange as range  # pylint: disable=W0622

from nicos_mlz.toftof.devices import calculations as calc
from nicos_mlz.toftof.devices.chopper.base import BaseChopperController


class Disc(VirtualMotor):

    parameters = {
        'phase': Param('Phase in respect to the first disc',
                       type=floatrange(-180, 180), default=0, settable=True,
                       ),
        'gear': Param('Gear', type=float, default=1, settable=True,),
        'crc': Param('Counter-rotating mode', type=int, default=1,
                     settable=True,),
        'slittype': Param('Slit type', type=int, default=1, settable=True,),
    }

    parameter_overrides = {
        'abslimits': Override(default=(-27000, 27000), mandatory=False),
        'unit': Override(default='rpm', mandatory=False,),
        'jitter': Override(default=2),
        'curvalue': Override(default=6000),
    }


class Controller(BaseChopperController):
    """The main controller device of the chopper."""

    attached_devices = {
        'discs': Attach('Chopper discs', Disc, multiple=7),
    }

    def doInit(self, mode):
        if mode == SIMULATION or session.sessiontype == POLLER:
            return
        self._change('speed', self.speed)

    def _change(self, name, value):
        """Internal interface to change a chopper value."""
        if name == 'wavelength':
            self._setROParam('wavelength', round(value * 1000.0) / 1000.0)
        elif name == 'speed':
            assert 150 <= value <= 22000
            self._setROParam('speed', value)
        elif name == 'ratio':
            assert value in range(1, 11)
            self._setROParam('ratio', value)
        elif name == 'crc':
            assert value in [0, 1]
            self._setROParam('crc', value)
        elif name == 'slittype':
            assert value in [0, 1, 2]
            self._setROParam('slittype', value)
        # calculate new phases
        phases = [0]
        for ch in range(1, 8):
            phi = calc.phi(ch, self.speed, self.wavelength, self.crc,
                           self.slittype, self.ratio, self.ch5_90deg_offset)
            assert -180. <= phi <= 180.
            phases.append(phi)
        r1, r2 = (2, -1.0) if self.crc == 0 else (1, 1.0)

        self._attached_discs[0].move(self.speed)
        self._attached_discs[0].phase = phases[1]

        self._attached_discs[1].move(r2 * self.speed)
        self._attached_discs[1].phase = phases[2]
        self._attached_discs[1].gear = r1
        self._attached_discs[1].slittype = self.slittype + 1

        self._attached_discs[2].move(self.speed)
        self._attached_discs[2].gear = 1
        self._attached_discs[2].phase = phases[3]
        self._attached_discs[2].crc = self.crc + 1

        self._attached_discs[3].move(self.speed)
        self._attached_discs[3].phase = phases[4]
        self._attached_discs[3].gear = 1

        # XXX if ratio == 1 then speed = 0 ?
        if self.ratio > 1:
            if self.ratio < 9:
                self._attached_discs[4].move(
                    -self.speed * (self.ratio - 1) / self.ratio)
            else:
                self._attached_discs[4].move(
                    -self.speed * 7. / self.ratio)
        else:
            self._attached_discs[4].move(-self.speed)
        self._attached_discs[4].phase = phases[5]
        self._attached_discs[4].gear = self.ratio + 1

        self._attached_discs[5].move(self.speed)
        self._attached_discs[5].phase = phases[6]
        self._attached_discs[5].gear = 1

        self._attached_discs[6].move(r2 * self.speed)
        self._attached_discs[6].phase = phases[7]
        self._attached_discs[6].gear = r1

        self._setROParam('phases', phases)
        self._setROParam('changetime', currenttime())

    def _stop(self):
        for dev in self._attached_discs:
            dev.move(0)
            dev.phase = 45
        self._setROParam('speed', 0)
        self._setROParam('changetime', currenttime())

    def _readspeeds(self):
        return [abs(dev.read()) for dev in self._attached_discs]

    def _readspeeds_actual(self):
        return [abs(v) * 279.618375
                for v in self._readspeeds()]

    def _readphase(self, ch):
        return self._attached_discs[ch - 1].phase

    def doReset(self):
        speed = sum(self._readspeeds())
        if speed > 0.5:
            raise NicosError(self, 'Attention: It is strictly forbidden to '
                             'reset the chopper system if one or more discs '
                             'are running!')
        self._setROParam('changetime', currenttime())

    def doStatus(self, maxage=0):
        ret = []
        stval = status.OK

        # read speeds
        for ch in range(1, 8):
            if (self.crc == 0 and ch in [2, 7]) or ch == 5:
                r2 = -1.0
            else:
                r2 = 1.0
            speed = self._attached_discs[ch - 1].read() * r2
            rat = 1.0
            if ch == 5:
                if self.ratio > 1 and self.ratio <= 8:
                    rat = self.ratio / (self.ratio - 1.0)
                elif self.ratio > 8:
                    rat = self.ratio / 7.0
            nominal = self.speed / rat
            maxdelta = self.speed_accuracy / rat
            if abs(speed - nominal) > maxdelta:
                msg = 'ch %d: speed %.2f != nominal %.2f' % (ch, speed,
                                                             nominal)
                ret.append(msg)
                if self.isTimedOut():
                    stval = status.OK  # NOTREACHED
                    self.log.warning(msg)
                else:
                    stval = status.BUSY
        # read phases
        for ch in range(2, 8):
            phase = self._readphase(ch)
            phase_diff = abs(phase - self._attached_discs[ch - 1].phase)
            if phase_diff > self.phase_accuracy:
                if self.isTimedOut():
                    # Due to some problems with the electronics the phase of
                    # the chopper disc 5 may have a phase differs from real
                    # value in the range of 360 or 270 degrees
                    if ch == 5:
                        msg = 'cd 5 phase %.2f != %.2f' % (
                            phase, self.phases[ch])
                        if phase_diff >= 360:
                            if phase_diff % 360 <= self.phase_accuracy:
                                self.log.warning(msg)
                                continue
                        elif phase_diff > 180:
                            if phase_diff >= (360. - self.phase_accuracy) or \
                               abs(phase_diff - 270) <= self.phase_accuracy:
                                self.log.warning(msg)
                                continue
                        stval = status.ERROR
                    else:
                        stval = status.ERROR
                else:
                    stval = status.BUSY
                msg = 'ch %d: phase %s != nominal %s' % (
                    ch, phase, self.phases[ch])
                ret.append(msg)
                if self.isTimedOut():
                    stval = status.OK  # NOTREACHED
                    self.log.warning(msg)
                else:
                    stval = status.BUSY
        return stval, ', '.join(ret) or 'normal'

    @requires(level=ADMIN)
    def adjust(self, angle=0.0):
        while angle > 180.0:
            angle -= 360
        while angle < -180.0:
            angle += 360
        self._setROParam('phases', [0, -26, 1, 19, 13, 1, -13, 62])
        self._setROParam('speed', 0)
        for ch in range(1, 8):
            self._attached_discs[ch].move(self.speed)
            self._attached_discs[ch].phase = self._attached_discs[ch] + angle
        self._setROParam('changetime', currenttime())

    @requires(level=ADMIN)
    def chmoveto(self, ch, angle=0.0):
        while angle > 180.0:
            angle -= 360
        while angle < -180.0:
            angle += 360
        if ch < 1 or ch > 7:
            raise NicosError(self, 'invalid chopper number')
        self._adjust()
        self._setROParam('speed', 0)
        self._attached_discs[ch].move(self.speed)
        self._attached_discs[ch].phase = angle
        self._setROParam('changetime', currenttime())

    @requires(level=ADMIN)
    def chrun(self, ch, speed=0):
        ds = round(speed)
        if ds < -22000 or ds > 22000:
            raise NicosError(self, 'disc speed out of safety limits')
        self._discSpeed = ds / 7.0
        if ch < 1 or ch > 7:
            raise NicosError(self, 'invalid chopper number')
        self._attached_discs[ch].move(ds)
        self._setROParam('changetime', currenttime())
