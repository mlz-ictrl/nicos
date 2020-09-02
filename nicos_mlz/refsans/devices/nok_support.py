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
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

from nicos.core import AutoDevice, ConfigurationError, HasPrecision, Moveable,\
    MoveError, Readable, dictwith, status
from nicos.core.errors import HardwareError
from nicos.core.params import Attach, Override, Param, floatrange, limits, \
    none_or, oneof, tupleof
from nicos.core.utils import multiReset
from nicos.devices.abstract import CanReference, Coder
from nicos.devices.generic import Axis
from nicos.devices.generic.sequence import SeqDev, SeqMethod, SequenceItem, \
    SequencerMixin
from nicos.devices.tango import Sensor
from nicos.utils import clamp, lazy_property

from nicos_mlz.refsans.devices.mixins import PolynomFit, PseudoNOK

MODES = ['ng', 'rc', 'vc', 'fc']


class NOKMonitoredVoltage(Sensor):
    """Return a scaled and monitored Analogue value.

    Also checks the value to be within certain limits, if not, complain.
    """

    parameters = {
        'reflimits': Param('None or Limits to check the reference: low, warn, '
                           'high',
                           type=none_or(tupleof(float, float, float)),
                           settable=False, default=None),
        'scale': Param('Scaling factor', type=float, settable=False,
                       default=1.),
    }
    parameter_overrides = {
        'unit': Override(default='V', mandatory=False),
    }

    def doInit(self, mode):
        if self.reflimits is not None:
            if not (0 <= self.reflimits[0] <= self.reflimits[1] <=
                    self.reflimits[2]):
                raise ConfigurationError(self, 'reflimits must be in ascending'
                                         ' order!')

    def doRead(self, maxage=0):
        value = self.scale * Sensor.doRead(self, maxage)
        if self.reflimits is not None:
            if abs(value) > self.reflimits[2]:
                raise HardwareError(self, 'Reference voltage (%.2f) above '
                                    'maximum (%.2f)' % (value,
                                                        self.reflimits[2]))
            if abs(value) < self.reflimits[0]:
                raise HardwareError(self, 'Reference voltage (%.2f) below '
                                    'minimum (%.2f)' % (value,
                                                        self.reflimits[0]))
            if abs(value) < self.reflimits[1]:
                self.log.warning('Reference voltage (%.2f) seems rather low, '
                                 'should be above %.2f', value,
                                 self.reflimits[1])
        return value

    def doStatus(self, maxage=0):
        try:
            self.doRead(maxage)
            return Sensor.doStatus(self, maxage)
        except HardwareError as err:
            return status.ERROR, repr(err)


class NOKPosition(PolynomFit, Coder):
    """Device to read the current Position of a NOK.

    The Position is determined by a ratiometric measurement between two
    analogue voltages measured with i7000 modules via taco.

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
# support stuff for the NOK
#

class SeqMoveOffLimitSwitch(SequenceItem):
    """Fancy SequenceItem.

    If the given device is at a limit switch, move it a little, else do nothing
    """

    def __init__(self, dev, *args, **kwargs):
        SequenceItem.__init__(self, dev=dev, args=args, kwargs=kwargs)

    def check(self):
        pass

    def run(self):
        if 'limit switch - active' in self.dev.status(0)[1]:
            # use 0.5 as fallback value
            self.dev.start(self.kwargs.get('backoffby', 0.5))

    def isCompleted(self):
        self.dev.wait()
        return True

    def __repr__(self):
        return 'MoveAwayFromLimitSwitch'


class SeqDevMin(SeqDev):
    """Fancy Sequenceitem.

    Same as SeqDev, but do not go below usermin.
    """

    def __init__(self, dev, target):
        # limit the position to allowed values
        target = clamp(target, dev.usermin, dev.usermax)
        SeqDev.__init__(self, dev, target)


#
# Nicos classes: for NOK's
#

# below code is based upon old nicm_nok.py
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
                     Moveable):
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

    def doInit(self, mode):
        for name, idx, ido in [('reactor', 0, 1),
                               ('sample', 1, 0)]:
            self.__dict__[name] = DoubleMotorAxis('%s.%s' % (self.name, name),
                                                  unit=self.unit,
                                                  both=self,
                                                  lowlevel=True,
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

        for dev in self._devices:
            res = dev.isAllowed(target_r)
            if not res[0]:
                return res

        # no problems detected, so it should be safe to go there....
        return True, ''

    def doIsAtTarget(self, pos, targets):
        traveldists = [target - (akt + ofs)
                       for target, akt, ofs in zip(targets, pos, self.offsets)]
        self.log.debug('doIsAtTarget', targets, 'traveldists', traveldists)
        return max(abs(v) for v in traveldists) <= self.precision

    def doStop(self):
        SequencerMixin.doStop(self)
        for dev in self._devices:
            dev.stop()
        try:
            self.wait()
        finally:
            self.reset()

    def doStart(self, targets):
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
        if self.isAtTarget(target=targets):
            return

        # XXX: backlash correction and repositioning later
        # build a moving sequence
        self.log.debug('mode: %s', self.mode)
        sequence = [SeqDev(d, t + ofs + self.masks[self.mode], stoppable=True)
                    for d, t, ofs in zip(self._devices, targets, self.offsets)]

        # now go to target again
        sequence += [SeqDev(d, t + ofs + self.masks[self.mode], stoppable=True)
                     for d, t, ofs in zip(self._devices, targets, self.offsets)]

        self.log.debug('Seq_3: %r', sequence)
        self._startSequence(sequence)

    def doReset(self):
        multiReset(self._motors)

    def doWriteMode(self, mode):
        self.log.debug('DoubleMotorNOK arg:%s  self:%s', mode, self.mode)
        target = self.doRead(0)
        self.log.debug('DoubleMotorNOK target %s', target)
        target = [pos + self.masks[mode] for pos in target]
        self.log.debug('DoubleMotorNOK target %s', target)
        sequence = [SeqDev(d, t + ofs, stoppable=True)
                    for d, t, ofs in zip(self._devices, target, self.offsets)]
        self.log.debug('Seq_4: %r', sequence)
        self._startSequence(sequence)

    def doStatus(self, maxage=0):
        self.log.debug('DoubleMotorNOK status')
        lowlevel = SequencerMixin.doStatus(self, maxage)
        if lowlevel[0] == status.BUSY:
            return lowlevel
        return Moveable.doStatus(self, maxage)


class DoubleMotorNOKIPC(DoubleMotorNOK):

    def doReference(self):
        """Reference the NOK in a sophisticated way.

        First we try to reach the lowest point ever needed for referencing,
        then we reference the lower refpoint first, and the higher later.
        After referencing is done, we go to (0, 0).
        """
        # XXX: EXTRA BIG TODO !!!
        if self._seq_is_running():
            raise MoveError(self, 'Cannot reference device, it is still '
                            'moving!')

        devices = self._devices
        refpos = [d.refpos for d in devices]

        # referencing is easier if device[0].refpos is always lower than
        #  device[1].refpos
        if refpos[1] < refpos[0]:
            # wrong order: flip oder of entries
            devices.reverse()
            refpos.reverse()

        # go below lowest interesting point
        minpos = min(self.read() + refpos + [t + self.backlash
                                             for t in refpos])

        # build a referencing sequence
        # go to lowest position first
        sequence = [SeqDevMin(d, minpos) for d in devices]

        # if one of the motors should have triggered the low-level-switch
        # move them up a little and wait until the movement has finished
        sequence += [SeqMoveOffLimitSwitch(d, backoffby=self.backlash / 4.)
                     for d in devices]

        # ref lowest position, should finish at refpos[0]
        # The move should be first, as the referencing may block!
        sequence += [SeqDev(devices[1], refpos[0]),
                     SeqMethod(devices[0], 'reference')]

        # ref highest position, should finish at refpos[1]
        sequence += [SeqDev(devices[0], refpos[1]),
                     SeqMethod(devices[1], 'reference')]

        # fun: move both to 0
        sequence += [SeqDev(d, 0) for d in devices]

        # GO
        self.log.debug('Seq_4: %r', sequence)
        self._startSequence(sequence)


class MotorEncoderDifference(Readable):

    attached_devices = {
        'motor': Attach('moving motor', Moveable),
        'analog': Attach('analog encoder maybe poti', Readable),
    }

    parameters = {
        'absolute': Param('Value is absolute or signed.', type=bool,
                          settable=True, default=True),
    }

    def doRead(self, maxage=0):
        dif = self._attached_analog.read(maxage) - \
            self._attached_motor.read(maxage)
        return abs(dif) if self.absolute else dif

    def doStatus(self, maxage=0):
        return status.OK, ''
