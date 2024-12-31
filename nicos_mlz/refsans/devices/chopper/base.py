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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Chopper related devices."""

from nicos.core import HasLimits, HasPrecision, Moveable, Override, Param, \
    dictwith, floatrange, intrange, status
from nicos.core.mixins import DeviceMixinBase, IsController
from nicos.core.params import Attach, limits, oneof
from nicos.devices.abstract import CanReference
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqParam

from nicos_mlz.refsans.lib.calculations import chopper_config


class SeqSlowParam(SeqParam):
    """Set a parameter of a device and check it until value is set.

    Some parameters change some hardware settings and this may take time.
    """

    def run(self):
        setattr(self.dev, self.paramname, self.value)

    def isCompleted(self):
        return getattr(self.dev, self.paramname) == self.value


class SeqFuzzyParam(SeqParam):
    """Set a parameter of a device and check the value with a precision."""

    def __init__(self, dev, paramname, value, precision=None):
        self.precision = precision
        SeqParam.__init__(self, dev=dev, paramname=paramname, value=value)

    def run(self):
        setattr(self.dev, self.paramname, self.value)

    def isCompleted(self):
        return True  # for known bug in firmware
        # value = getattr(self.dev, self.paramname)
        # if self.precision is None:
        #     return value == self.value
        # return abs(value - self.value) <= self.precision


class ChopperMaster(CanReference, BaseSequencer):

    valuetype = dictwith(
        wlmin=floatrange(0, 30),
        wlmax=floatrange(0, 30),
        gap=floatrange(0, 100),
        chopper2_pos=intrange(1, 6),
        D=float,
        manner=oneof('normal', 'parasitic'),
    )

    parameters = {
        'mode': Param('Chopper operation mode (normal, virtual6)',
                      type=oneof('normal_mode', 'virtual_disc2_pos_6'),
                      settable=False, category='status'),
        'manner': Param('Chopper interface mode (normal, parasitic)',
                        type=oneof('normal', 'parasitic'),
                        settable=True, category='status', default='normal'),
        'delay': Param('Delay for start signal in deg',
                       type=floatrange(-360, 360), settable=True,
                       userparam=True),
        'wlmin': Param('Mimimum of wavelength',
                       type=floatrange(0, 30), settable=True, userparam=True,
                       unit='AA', category='status'),
        'wlmax': Param('Maximum of wavelength',
                       type=floatrange(0, 30), settable=True, userparam=True,
                       unit='AA', category='status'),
        'dist': Param('flight path (distance chopper disc 1 to detector)',
                      type=floatrange(0), settable=True, userparam=True,
                      unit='m', category='status'),
        'gap': Param('Gap ... ',
                     type=floatrange(0, 100), settable=True, userparam=True,
                     unit='%', category='status'),
        'speed': Param('Chopper1 speed ... ',
                       type=floatrange(0), settable=False, userparam=True,
                       mandatory=False, volatile=True, category='status'),
    }

    _max_disks = 6

    attached_devices = {
        'chopper1': Attach('chopper1 defining speed', Moveable),
        'chopper2': Attach('chopper2 phase', Moveable),
        'chopper3': Attach('chopper3 phase also height', Moveable),
        'chopper4': Attach('chopper4 phase also height', Moveable),
        'chopper5': Attach('chopper5 phase half speed', Moveable),
        'chopper6': Attach('chopper6 phase half speed', Moveable),
        'shutter': Attach('Shutter device', Moveable),
    }

    def doInit(self, mode):
        self._choppers = (self._attached_chopper1, self._attached_chopper2,
                          self._attached_chopper3, self._attached_chopper4,
                          self._attached_chopper5, self._attached_chopper6)

    def _generateSequence(self, target):
        self.log.info('_generateSequence')
        self.wlmin, self.wlmax = limits((target.get('wlmin', self.wlmin),
                                         target.get('wlmax', self.wlmax)))
        self.dist = target.get('D', self.dist)
        self.gap = target.get('gap', self.gap)
        self.manner = target.get('manner', self.manner)
        chopper2_pos = target.get('chopper2_pos')

        self.log.info('analysis manner = %s', self.manner)
        suppress_parasitic = self.manner == 'normal'
        self.log.info('suppress_parasitic = %s', suppress_parasitic)

        speed, angles, disc2_out, D_o, wl_min_o, wl_max_o = chopper_config(
            self.wlmin, self.wlmax, self.dist, chopper2_pos, gap=self.gap,
            suppress_parasitic=suppress_parasitic)
        if speed is None:
            line = 'None'
        else:
            line = 'speed: %d, ' % speed
            line += 'disc2_out = %d,' % disc2_out
            line += 'angles = %s ' % angles
            line += 'D: %f, ' % D_o
            line += 'wl_min: %f, ' % wl_min_o
            line += 'wl_max: %f, ' % wl_max_o
        self.log.info(line)

        seq = []
        self.log.warning('BLOCKED')
        # return seq
        shutter_pos = self._attached_shutter.read(0)
        shutter_ok = self._attached_shutter.status(0)[0] == status.OK
        # if chopper2_pos == 6:
        if self.manner == 'parasitic':
            self._setROParam('mode', 'virtual_disc2_pos_6')
        else:
            if chopper2_pos != disc2_out:
                self.log.info('automatic changing chopper2_pos from %d to %d',
                              chopper2_pos, disc2_out)
                chopper2_pos = disc2_out
            self._setROParam('mode', 'normal_mode')
            chopper2_pos_akt = self._attached_chopper2.pos
            if chopper2_pos_akt != chopper2_pos:
                if shutter_ok:
                    seq.append(SeqDev(self._attached_shutter, 'closed',
                                      stoppable=True))
                seq.append(SeqDev(self._attached_chopper1, 0, stoppable=True))
                seq.append(SeqSlowParam(self._attached_chopper2, 'pos',
                                        chopper2_pos))

        for dev, t in zip(self._choppers[1:], angles[1:]):
            # The Chopper measures the phase in the opposite direction
            # as we do this was catered for here, we have moved the
            # sign conversion to the doWritePhase function
            # dev.phase = -t  # sign by history
            seq.append(SeqFuzzyParam(dev, 'phase', t, 0.5))
        seq.append(SeqDev(self._attached_chopper1, speed, stoppable=True))
        if shutter_ok:
            seq.append(SeqDev(self._attached_shutter, shutter_pos,
                              stoppable=True))
        # for line in seq:
        #     self.log.info(line)
        # self.log.warning('BLOCKED Debug MP only')
        # return []
        return seq

    def doRead(self, maxage=0):
        # TODO: for cfg
        value = {
            'D': self.dist,
            'wlmin': self.wlmin,
            'wlmax': self.wlmax,
            'gap': self.gap,
            'chopper2_pos':
                self._attached_chopper2.pos
                if self.mode == 'normal_mode' else 6,
            'manner': self.manner,
        }
        return value

    def _getWaiters(self):
        return self._choppers

    def doReadResolution(self):
        if self.mode == 'normal_mode':
            return self._attached_chopper2.pos
        return 6

    def doReadSpeed(self):
        return self._attached_chopper1.read(0)


class ChopperDisc(HasLimits, HasPrecision, DeviceMixinBase):

    parameters = {
        'phase': Param('Phase of chopper disc',
                       type=floatrange(0, 360), settable=True, userparam=True,
                       fmtstr='%.2f', unit='deg', category='status'),
        'current': Param('motor current',
                         type=float, settable=False, volatile=True,
                         userparam=True, fmtstr='%.2f', unit='A'),
        'mode': Param('Internal mode',
                      type=int, settable=False, userparam=True),
        'chopper': Param('chopper number inside controller',
                         type=intrange(1, 6), settable=False, userparam=True),
        'reference': Param('reference to Disc one',
                           type=floatrange(-360, 360), settable=False,
                           userparam=True),
        'edge': Param('Chopper edge of neutron window',
                      type=oneof('open', 'close'), settable=False,
                      userparam=True),
        'gear': Param('Chopper ratio',
                      type=intrange(-6, 6), settable=False, userparam=True,
                      default=0),
        'pos': Param('Distance to the disc 1',
                     type=floatrange(0), settable=False, userparam=True,
                     default=0., fmtstr='%.2f', unit='m', category='status'),
    }

    parameter_overrides = {
        'unit': Override(default='rpm', mandatory=False,),
        'precision': Override(default=2),
        'abslimits': Override(default=(0, 6000), mandatory=False),
        'fmtstr': Override(default='%.f'),
    }

    def doPoll(self, n, maxage):
        self._pollParam('current')

    def _isStopped(self):
        return abs(self.read(0)) <= self.precision


class ChopperDisc2(DeviceMixinBase):
    """Chopper disc device with translation."""

    parameter_overrides = {
        'pos': Override(settable=True, type=intrange(1, 5), fmtstr='%d',
                        volatile=True, default=intrange(1, 5)(), unit=''),
    }

    attached_devices = {
        'translation': Attach('Chopper disc device', Moveable),
    }

    def doWritePos(self, target):
        self._attached_translation.move(target)

    def doReadPos(self):
        return self._attached_translation.read(0)


class ChopperDiscTranslation(CanReference, IsController, DeviceMixinBase):
    """Position of chopper disc along the x axis.

    Since the chopper disc can be translated, the chopper speed must be low
    enough (around 0, defined by its precision).

    The change of speed must be blocked if the translation device is not at
    a defined position.
    """

    valuetype = intrange(1, 5)

    attached_devices = {
        'disc': Attach('Chopper disc device', Moveable),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'abslimits': Override(mandatory=False, default=limits((1, 5))),
        'fmtstr': Override(default='%d'),
    }

    def doReference(self, *args):
        self.move(1)

    def doIsAllowed(self, target):
        if self._attached_disc._isStopped():
            return True, ''
        return False, 'Disc (%s) speed is too high, %.0f!' % (
            self._attached_disc, self.read(0))

    def isAdevTargetAllowed(self, adev, adevtarget):
        state = self.status(0)
        if state[0] == status.OK:
            return True, ''
        return False, 'translation is: %s' % state[1]

    def _getWaiters(self):
        return []
