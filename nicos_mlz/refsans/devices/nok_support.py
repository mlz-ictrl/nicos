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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

from nicos.core import AutoDevice, HasAutoDevices, HasPrecision, Moveable, \
    MoveError, Readable, dictwith, status
from nicos.core.params import Attach, Override, Param, floatrange, limits, \
    oneof, tupleof
from nicos.core.utils import multiReset
from nicos.devices.abstract import CanReference, Coder
from nicos.devices.generic import Axis
from nicos.devices.generic.sequence import SequencerMixin
from nicos.utils import lazy_property

from nicos_mlz.refsans.devices.mixins import PolynomFit, PseudoNOK

MODES = ['ng', 'rc', 'vc', 'fc']


class NOKPosition(PolynomFit, Coder):
    """Device to read the current Position of a NOK.

    The Position is determined by a ratiometric measurement between two
    analogue voltages measured with i7000 modules via Tango.

    As safety measure, the reference voltage obtained is checked to be in some
    configurable limits.
    """

    attached_devices = {
        'measure': Attach('Sensing Device (Poti)', Readable),
        'reference': Attach('Reference Device', Readable),
    }

    parameters = {
        'length': Param('Length... ????',
                        type=float, mandatory=False),
        # fun stuff, not really needed....
        'serial': Param('Serial number',
                        type=int, mandatory=False),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.3f'),
        'unit': Override(default='mm', mandatory=False),
    }

    hardware_access = False

    def doReset(self):
        multiReset(self._adevs)

    def doRead(self, maxage=0):
        """Read basically two (scaled) voltages.

         - value from the poti (times a sign correction for top mounted potis)
         - ref from a reference voltage, scaled by 2 (Why???)

        Then it calculates the ratio poti / ref.
        Then this is put into a correcting polynom of at least first order
        Result is then offset + mul * <previously calculated value>
        """
        poti = self._attached_measure.read(maxage)
        ref = self._attached_reference.read(maxage)

        self.log.debug('Poti vs. Reference value: %f / %f', poti, ref)
        # apply simple scaling
        return self._fit(poti / ref)

#
# Nicos classes: for NOK's
#


class SingleMotorNOK(PseudoNOK, Axis):
    """NOK using a single axis.

    Basically a generic NICOS axis with precision
    """

    parameters = {
        'nok_motor': Param('Position of the motor for this nok', type=float,
                           settable=False, unit='mm', category='general'),
    }


class DoubleMotorAxis(AutoDevice, Moveable):
    """NOK using two axes.
    BrotherMotor
    DEVELOPING MP only
    """
    attached_devices = {
        'both': Attach('access to both of them via mode', Moveable),
    }

    parameters = {
        'index': Param('right side of nok', type=oneof(0, 1),
                       settable=False, mandatory=True),
        'other': Param('other side of nok', type=oneof(0, 1),
                       settable=False, mandatory=True),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        return self._attached_both.read(maxage=maxage)[self.index]

    def doStatus(self, maxage=0):
        return self._attached_both.status(maxage=maxage)

    def doStart(self, target):
        incmin, incmax = self._attached_both.inclinationlimits
        brother = self._attached_both.read(0)[self.other]
        inclination = target - brother
        if incmin > inclination:
            brother = target - incmin / 2
        elif incmax < inclination:
            brother = target - incmax / 2
        else:
            pass  # legal driving range nothing to do
        if self.other == 1:
            self._attached_both.move([target, brother])
        else:
            self._attached_both.move([brother, target])


class DoubleMotorNOK(SequencerMixin, CanReference, PseudoNOK, HasPrecision,
                     HasAutoDevices, Moveable):
    """NOK using two axes.

    If backlash is negative, approach form the negative side (default),
    else approach from the positive side.
    If backlash is zero, don't mind and just go to the target.
    """

    attached_devices = {
        'motor_r': Attach('NOK moving motor, reactor side', Moveable),
        'motor_s': Attach('NOK moving motor, sample side', Moveable),
    }

    parameters = {
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='ng', category='experiment'),
        'nok_motor': Param('Position of the motor for this NOK',
                           type=tupleof(float, float), settable=False,
                           unit='mm', category='general'),
        'inclinationlimits': Param('Allowed range for the positional '
                                   'difference',
                                   type=limits, mandatory=True),
        'backlash': Param('Backlash correction in phys. units',
                          type=float, default=0., unit='main'),
        'offsets': Param('Offsets of NOK-Motors (reactor side, sample side)',
                         type=tupleof(float, float), default=(0., 0.),
                         settable=False, unit='main', category='offsets'),
    }

    parameter_overrides = {
        'precision': Override(type=floatrange(0, 100)),
        'masks': Override(type=dictwith(**{name: float for name in MODES}),
                          unit='', mandatory=True),
    }

    valuetype = tupleof(float, float)
    _honor_stop = True
    hardware_access = False

    def doInit(self, mode):
        for name, idx, ido in [('reactor', 0, 1),
                               ('sample', 1, 0)]:
            self.add_autodevice(name,
                                DoubleMotorAxis,
                                unit=self.unit,
                                both=self,
                                visibility=(),
                                index=idx,
                                other=ido)
        self._motors = [self._attached_motor_r, self._attached_motor_s]

    @lazy_property
    def _devices(self):
        return self._attached_motor_r, self._attached_motor_s

    def doRead(self, maxage=0):
        return [dev.read(maxage) - ofs - self.masks[self.mode]
                for dev, ofs in zip(self._devices, self.offsets)]

    def doIsAllowed(self, targets):
        target_r, target_s = targets
        target_r += self.offsets[0]
        target_s += self.offsets[1]

        incmin, incmax = self.inclinationlimits

        inclination = target_s - target_r
        if not incmin < inclination < incmax:
            return False, 'Inclination %.2f out of limit (%.2f, %.2f)!' % (
                inclination, incmin, incmax)

        for dev, tar in zip(self._devices, targets):
            res = dev.isAllowed(tar)
            if not res[0]:
                return res

        # no problems detected, so it should be safe to go there....
        return True, ''

    def doIsAtTarget(self, pos, target):
        traveldists = [t - (akt + ofs)
                       for t, akt, ofs in zip(target, pos, self.offsets)]
        self.log.debug('doIsAtTarget %s traveldists %s', target, traveldists)
        return max(abs(v) for v in traveldists) <= self.precision

    def doStop(self):
        SequencerMixin.doStop(self)
        for dev in self._devices:
            dev.stop()
        try:
            self.wait()
        finally:
            self.reset()

    def doStart(self, target):
        """Generate and start a sequence if none is running.

        The sequence is optimised for negative backlash.
        It will first move both motors to the lowest value of
        (target + backlash, current_position) and then
        to the final target.
        So, inbetween, the NOK should be parallel to the beam.
        """
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')

        # check precision, only move if needed!
        if self.isAtTarget(target=target):
            return

        # XXX: backlash correction and repositioning later
        self.log.debug('mode: %s', self.mode)
        for d, t, ofs in zip(self._devices, target, self.offsets):
            d.move(t + ofs + self.masks[self.mode])

    def doReset(self):
        multiReset(self._motors)

    def doWriteMode(self, mode):
        pass
        # self.log.debug('DoubleMotorNOK arg:%s  self:%s', mode, self.mode)
        # target = self.doRead(0)
        # self.log.debug('DoubleMotorNOK target %s', target)
        # target = [pos + self.masks[mode] for pos in target]
        # self.log.debug('DoubleMotorNOK target %s', target)
        # sequence = [SeqDev(d, t + ofs, stoppable=True)
        #             for d, t, ofs in zip(self._devices, target, self.offsets)]
        # self.log.debug('Seq_4: %r', sequence)
        # self._startSequence(sequence)

    def doStatus(self, maxage=0):
        self.log.debug('DoubleMotorNOK status')
        lowlevel = SequencerMixin.doStatus(self, maxage)
        if lowlevel[0] == status.BUSY:
            return lowlevel
        return Moveable.doStatus(self, maxage)
