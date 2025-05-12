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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for Refsans slits."""

import numpy as np

from nicos.core import Attach, AutoDevice, Moveable, Override, Param, Value, \
    dictof, dictwith, floatrange, oneof, status, tupleof
from nicos.core.mixins import HasOffset, HasPrecision
from nicos.core.utils import devIter
from nicos.devices.generic import ManualSwitch
from nicos.devices.generic.sequence import BaseSequencer, SeqDev
from nicos.utils import lazy_property

from nicos_mlz.refsans.devices.mixins import PseudoNOK

SLIT = 'slit'
POINT = 'point'
GISANS = 'gisans'
MODES = [SLIT, POINT, GISANS]
CENTERED = 'centered'


class SingleSlit(PseudoNOK, HasPrecision, HasOffset, Moveable):
    """Slit using one axis."""

    hardware_access = False

    attached_devices = {
        'motor': Attach('moving motor', Moveable),
    }

    parameters = {
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='slit', category='general'),
        '_offsets': Param('List of offsets per mode position',
                          settable=False, internal=True,
                          type=dictof(str, float), default={}),
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(CENTERED), userparam=True, settable=True,
                        default=CENTERED, category='experiment'),
    }

    parameter_overrides = {
        'masks': Override(type=dictwith(**{name: float for name in MODES}),
                          unit='', mandatory=True),
        'precision': Override(default=0.01),
    }

    valuetype = float

    def doWriteOffset(self, value):
        self.log.debug('use of doWriteOffset')
        HasOffset.doWriteOffset(self, value)
        # deep copy is need to be able to change the values
        d = self._offsets.copy()
        d[self.mode] = value
        self._setROParam('_offsets', d)

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage) - self.masks[self.mode] - \
            self.offset

    def doIsAllowed(self, target):
        return self._attached_motor.isAllowed(target + self.masks[self.mode])

    def doStop(self):
        self._attached_motor.stop()

    def doStart(self, target):
        self._attached_motor.start(
            target + self.masks[self.mode] + self.offset)

    def doWriteMode(self, mode):
        pass
        # self._attached_motor.start(self._attached_motor.read(0) +
        #                            self.masks[mode] - self.masks[self.mode])
        # update the offset parameter from offset mapping
        # self._setROParam('offset', self._offsets.get(mode, 0.))
        # self.log.debug('New offset is now: %f', self.offset)


class DoubleSlit(PseudoNOK, Moveable):
    """Double slit using two SingleSlits."""

    hardware_access = False

    attached_devices = {
        'slit_r': Attach('Reactor side single slit', SingleSlit),
        'slit_s': Attach('Sample side single slit', SingleSlit),
    }

    parameters = {
        'mode': Param('Modus of Beam',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='slit', category='experiment'),
        'maxheight': Param('Max opening of the slit',
                           type=floatrange(0), settable=False, default=12.),
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(CENTERED),  # '2blades' is possible
                        userparam=True, settable=True, default=CENTERED,
                        category='experiment'),
    }

    parameter_overrides = {
        'nok_start': Override(volatile=True),
        'nok_end': Override(volatile=True),
    }

    def doInit(self, mode):
        # Even if the slit could not be become closer than 0 and not more
        # opened the maxheight the instrument scientist want to scan over
        # the limits to find out the 'open' and 'closed' point for the neutrons
        self.valuetype = tupleof(float, floatrange(-1, self.maxheight + 1))
        # generate auto devices
        for name, idx, opmode in [('center', 0, CENTERED),
                                  ('opening', 1, CENTERED)]:
            self.__dict__[name] = SingleSlitAxis('%s.%s' % (self.name, name),
                                                 slit=self, unit=self.unit,
                                                 visibility=(), index=idx,
                                                 opmode=opmode)
        self._motors = [self._attached_slit_r, self._attached_slit_s]

    def doStatus(self, maxage=0):
        st = Moveable.doStatus(self, maxage)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def doWriteMode(self, mode):
        for d in self._motors:
            d.mode = mode

    def _calculate_slits(self, arg, direction):
        self.log.debug('calculate slits: dir:%s mode:%s arg %s', direction,
                       self.mode, str(arg))
        if direction:
            reactor, sample = arg
            opening = self.maxheight - (sample - reactor)
            center = (sample + reactor) / 2.0
            res = [center, opening]
        else:
            center, opening = arg
            reactor = center - (self.maxheight - opening) / 2.0
            sample = center + (self.maxheight - opening) / 2.0
            res = [reactor, sample]
        self.log.debug('res %s', res)
        return res

    def doRead(self, maxage=0):
        return self._calculate_slits([self._attached_slit_r.read(maxage),
                                      self._attached_slit_s.read(maxage)],
                                     True)

    def doIsAllowed(self, targets):
        self.log.debug('DoubleSlit doIsAllowed %s', targets)
        why = []
        try:
            self.valuetype((targets[0], 0))
        except ValueError as e:
            why.append('%s' % e)
        for dev, pos in zip(self._motors,
                            self._calculate_slits(targets, False)):
            ok, _why = dev.isAllowed(pos)
            if not ok:
                why.append('%s: requested position %.3f %s out of limits; %s'
                           % (dev, pos, dev.unit, _why))
            else:
                self.log.debug('%s: requested position %.3f %s allowed', dev,
                               pos, dev.unit)
        if why:
            return False, '; '.join(why)
        return True, ''

    def doStop(self):
        for dev in self._adevs.values():
            dev.stop()

    def doStart(self, targets):
        """Generate and start a sequence if none is running."""
        for dev, target in zip([self._attached_slit_r, self._attached_slit_s],
                               self._calculate_slits(targets, False)):
            dev.start(target)

    def doReadNok_Start(self):
        return self._attached_slit_r.nok_start

    def doReadNok_End(self):
        return self._attached_slit_s.nok_end

    def doPoll(self, n, maxage):
        # also poll sub-AutoDevices we created
        for dev in devIter(self.__dict__, baseclass=AutoDevice):
            dev.poll(n, maxage)

    def valueInfo(self):
        return (Value('%s.center' % self, unit=self.unit, fmtstr='%.2f'),
                Value('%s.height' % self, unit=self.unit, fmtstr='%.2f'))


class DoubleSlitSequence(BaseSequencer, DoubleSlit):

    attached_devices = {
        'adjustment': Attach('positioning Frame of b3h3', ManualSwitch),
    }

    def doStatus(self, maxage=0):
        self.log.debug('DoubleSlitSequence status')
        st = BaseSequencer.doStatus(self, maxage)
        if st[0] != status.OK:
            return st
        st = DoubleSlit.doStatus(self, maxage=maxage)
        self.log.debug('DoubleSlitSequence status %s', st)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def _generateSequence(self, target):
        """Generate and start a sequence if none is running.

        be sure not to cross the blades
        """

        self.log.debug('Frame %s %s', self._adjustment_offset(), target)

        center = self.center.read(0)
        dif = target[1] - center
        self.log.debug('safe %s dif %.2f center %.2f', target, dif, center)
        if True and False:  # pylint: disable=condition-evals-to-constant
            safe_seq = []
            step = (target[0] + .5001) * np.sign(dif)
            akt = center + step
            while True:
                if akt == target[1]:
                    safe_seq.append([target[0], akt])
                    break
                if dif > 0:
                    if akt > target[1]:
                        safe_seq.append([target[0], target[1]])
                        break
                else:
                    if akt < target[1]:
                        safe_seq.append([target[0], target[1]])
                        break
                safe_seq.append([target[0], akt])
                akt += step
            sequence = []
            for s in safe_seq:
                targets = self._calculate_slits(s, False)
                self.log.debug('seq  %s targets %s', s, targets)
                if dif > 0:
                    sequence += [
                        SeqDev(self._attached_slit_s, targets[1],
                               stoppable=True),
                        SeqDev(self._attached_slit_r, targets[0],
                               stoppable=True),
                    ]
                else:
                    sequence += [
                        SeqDev(self._attached_slit_r, targets[0],
                               stoppable=True),
                        SeqDev(self._attached_slit_s, targets[1],
                               stoppable=True),
                    ]
            self.log.info('Seq len: %d', len(sequence))
        else:
            targets = self._calculate_slits(target, False)
            if dif < 0:
                self.log.debug('swap sequence')
                sequence = [
                    SeqDev(self._attached_slit_s, targets[1],
                           stoppable=True),
                    SeqDev(self._attached_slit_r, targets[0],
                           stoppable=True),
                ]
            else:
                self.log.debug('orginal sequence')
                sequence = [
                    SeqDev(self._attached_slit_r, targets[0],
                           stoppable=True),
                    SeqDev(self._attached_slit_s, targets[1],
                           stoppable=True),
                ]
            self.log.debug('Seq_2: %r', sequence)
        return sequence

    def _adjustment_offset(self):
        return int(self._attached_adjustment.read(0)[:-2]) - 110

    def doRead(self, maxage=0):
        pos = DoubleSlit.doRead(self, maxage=maxage)
        self.log.debug('Frame %s %d', pos, self._adjustment_offset())
        return pos


class SingleSlitAxis(AutoDevice, Moveable):

    valuetype = float

    hardware_access = False

    attached_devices = {
        'slit': Attach('Slit whose axis is controlled', Moveable),
    }

    parameters = {
        'index': Param('Which index of the super slit is used for this device',
                       type=int, userparam=False),
        'opmode': Param('Mode of the super slit to be used for this device',
                        type=str, userparam=False, category='experiment'),
    }

    @lazy_property
    def slit(self):
        return self._attached_slit

    def _conv(self, target):
        """convert our target value to target values for the main slit axis"""
        pos = list(self.slit.target if self.slit.target else self.slit.read())
        pos[self.index] = target
        return tuple(pos)

    def doRead(self, maxage=0):
        """read main slit's raw values and convert to our opmode"""
        return self.slit.read(0)[self.index]

    def doStart(self, target):
        """convert our target value to target values for the main slit axis
         and start movement there"""
        self.slit.start(self._conv(target))

    def doIsAllowed(self, target):
        return self.slit.isAllowed(self._conv(target))
