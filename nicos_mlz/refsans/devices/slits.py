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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for Refsans slits."""

from __future__ import absolute_import, division, print_function

from nicos.core import SIMULATION, Attach, AutoDevice, Moveable, Override, \
    Param, Value, dictof, dictwith, floatrange, oneof, status, tupleof
from nicos.core.errors import MoveError
from nicos.core.mixins import HasOffset
from nicos.core.utils import devIter
from nicos.devices.generic.sequence import SeqDev, SequencerMixin
from nicos.utils import lazy_property

from nicos_mlz.refsans.devices.mixins import PseudoNOK

SLIT = 'slit'
POINT = 'point'
GISANS = 'gisans'
MODES = [SLIT, POINT, GISANS]
CENTERED = 'centered'


class SingleSlit(PseudoNOK, HasOffset, Moveable):
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
    }

    valuetype = float

    def doWriteOffset(self, value):
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
        self._attached_motor.start(self._attached_motor.read(0) +
                                   self.masks[mode] - self.masks[self.mode])
        # update the offset parameter from offset mapping
        self._setROParam('offset', self._offsets.get(mode, 0.))
        self.log.debug('New offset is now: %f', self.offset)


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
        # Even if the slit could not be become closer then 0 and not more
        # opened the maxheight the instrument scientist want to scan over
        # the limits to find out the 'open' and 'closed' point for the neutrons
        self.valuetype = tupleof(floatrange(-1, self.maxheight + 1), float)
        # generate auto devices
        for name, idx, opmode in [('height', 0, CENTERED),
                                  ('center', 1, CENTERED)]:
            self.__dict__[name] = SingleSlitAxis('%s.%s' % (self.name, name),
                                                 slit=self, unit=self.unit,
                                                 lowlevel=True, index=idx,
                                                 opmode=opmode)
        self._motors = [self._attached_slit_r, self._attached_slit_s]

    def doStatus(self, maxage=0):
        st = Moveable.doStatus(self, maxage)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def doWriteMode(self, mode):
        for d in self._adevs.values():
            d.mode = mode

    def _calculate_slits(self, arg, direction):
        self.log.debug('calculate slits: dir:%s mode:%s arg %s', direction,
                       self.mode, str(arg))
        if direction:
            reactor, sample = arg
            opening = self.maxheight - (sample - reactor)
            height = (sample + reactor) / 2.0
            res = [opening, height]
        else:
            opening, height = arg
            reactor = height - (self.maxheight - opening) / 2.0
            sample = height + (self.maxheight - opening) / 2.0
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
        for dev, pos in zip([self._attached_slit_r, self._attached_slit_s],
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

    # def doIsAtTarget(self, targets):
    #     # check precision, only move if needed!
    #     self.log.debug('DoubleSlit doIsAtTarget %s', targets)
    #     targets = self.rechnen_motor(targets, False, 'doIsAtTarget')
    #     self.log.debug('%s', targets)
    #     traveldists = [target - dev.doRead(0)
    #                    for target, dev in zip(targets, self._devices)]
    #     return max(abs(v) for v in traveldists) <= self.precision

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
        return Value('%s.height' % self, unit=self.unit, fmtstr='%.2f'), \
               Value('%s.center' % self, unit=self.unit, fmtstr='%.2f')


class DoubleSlitSequence(SequencerMixin, DoubleSlit):

    def doStart(self, target):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))

    def doStatus(self, maxage=0):
        st = SequencerMixin.doStatus(self, maxage)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def _generateSequence(self, target):
        """Generate and start a sequence if none is running.

        be sure not to cross the blades
        """

        targets = self._calculate_slits(target, False)
        if (target[1] - self.center.read(0)) < 0:
            self.log.debug('DoubleSlitSequence Seq swap')
            sequence = [
                SeqDev(self._attached_slit_s, targets[1], stoppable=True),
                SeqDev(self._attached_slit_r, targets[0], stoppable=True),
            ]
        else:
            self.log.debug('DoubleSlitSequence Seq org')
            sequence = [
                SeqDev(self._attached_slit_r, targets[0], stoppable=True),
                SeqDev(self._attached_slit_s, targets[1], stoppable=True),
            ]
        self.log.debug('Seq_2: %r', sequence)
        return sequence


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
