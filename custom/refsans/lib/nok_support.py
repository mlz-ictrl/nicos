#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Support Code for REFSANS's NOK's.
"""

import time


from nicos.core import status, Readable, Moveable, ConfigurationError, \
     HasPrecision, MoveError, DeviceMixinBase, status
from nicos.core.errors import ConfigurationError, HardwareError
from nicos.core.params import Param, Attach, Override, tupleof, \
     nonemptylistof, floatrange, intrange, limits, none_or
from nicos.core.utils import multiReset
from nicos.utils import clamp, lazy_property
from nicos.devices.abstract import CanReference, Coder
from nicos.devices.generic import Axis
from nicos.devices.generic.sequence import SequencerMixin, SeqDev, \
     SeqMethod, SequenceItem

from nicos.devices.vendor.ipc import Motor as IPCMotor

from nicos.devices.taco import AnalogInput


#
#
# The following stuff should go away in the future.
# It is here due to the 'disorganised' structure beeing used so far
# and because we can't change ALL of it in one go.
#
#

class PseudoNOK(DeviceMixinBase):
    """Placeholder device, doing nothing, but storing some locational data"""
    parameters = {
        'nok_start'  : Param('Start of the  NOK (ab NLE2b)', type=float, default=0,
                              settable=False, mandatory=False, unit='mm'),
        'nok_length' : Param('Length of the NOK', type=float, default=0,
                              settable=False, mandatory=False, unit='mm'),
        'nok_end'    : Param('End of the NOK (ab NLE2b)', type=float, default=0,
                              settable=False, mandatory=False, unit='mm'),
        'nok_gap'    : Param('Gap after the NOK (ab NLE2b)', type=float, default=0,
                              settable=False, mandatory=False, unit='mm'),
        'masks'      : Param('Masks for this NOK', type=dict, settable=False, default={}),
    }


class NOKMonitoredVoltage(AnalogInput):
    """returns a scaled and monitored Analog value

    Also checks the value to be within certain limits,
    if not, complain.
    """
    parameters = {
        'reflimits'   : Param('None or Limits to check the reference: low, warn, high',
                              type=none_or(tupleof(float,float,float)), settable=False, default=None),
        'scale'       : Param('Scaling factor', type=float, settable=False, default=1.),
    }
    parameter_overrides = {
        'unit'  : Override(default = 'V', mandatory=False),
    }

    def doInit(self, mode):
        if self.reflimits is not None:
            if not (0 <= self.reflimits[0] <= self.reflimits[1] <= self.reflimits[2]):
                raise ConfigurationError(self, 'reflimits must be in ascending order!')

    def doRead(self, maxage=0):
        value = self.scale * AnalogInput.doRead(self, maxage)
        if self.reflimits is not None:
            if abs(value) > self.reflimits[2]:
                raise HardwareError(self, 'Reference voltage (%.2f) above maximum (%.2f)' %
                                           (value, self.reflimits[2]))
            if abs(value) < self.reflimits[0]:
                raise HardwareError(self, 'Reference voltage (%.2f) below minimum (%.2f)' %
                                           (value, self.reflimits[0]))
            if abs(value) < self.reflimits[1]:
                self.log.warning('Reference voltage (%.2f) seems rather low, should be '
                                  'above %.2f' % (value, self.reflimits[1]))
        return value

    def doStatus(self, maxage=0):
        try:
            _ = self.doRead(maxage)
            return AnalogInput.doStatus(self, maxage)
        except HardwareError as err:
            return status.ERROR, repr(err)



class NOKPosition(Coder):
    """Device to read the current Position of a NOK

    The Position is determined by a ratiometric measurement between two analog voltages
    measured with i7000 modules via taco.

    As safety measure, the reference voltage obtained is checked to be in some configurable limits.
    """
    attached_devices = {
        'measure'       : Attach('Sensing Device (Poti)', Readable),
        'reference'     : Attach('Reference Device', Readable),
    }
    parameters = {
        'poly'            : Param('Polynomial coefficients in ascending order',
                                   type=nonemptylistof(float), settable=True,
                                   mandatory=True, default=0.),
        'length'          : Param('length... ????',
                                   type=float, mandatory=False),
        # fun stuff, not really needed....
        'serial'          : Param('serial number',
                                   type=int, mandatory=False),
    }

    parameter_overrides = {
        'fmtstr' : Override(default = '%.3f'),
        'unit'   : Override(default = 'mm', mandatory = False),
    }


    def doInit(self, mode):
        if len(self.poly) == 0:
            raise ConfigurationError(self,
                            'Need at least one Parmeter for correction polynom!')

    def doReset(self):
        multiReset(self._adevs)


    def doRead(self, maxage=0):
        """This basically reads two (scaled) voltages:
         - poti from the poti (times a sign correction for top mounted potis)
         - ref from a reference voltage, scaled by 2 (Why???)

        Then it calculates the ratio poti / ref.
        Then this is put into a correcting polynom of at least first order
        Result is then offset + mul * <previously calculated value>
        """
        poti = self._attached_measure.read(maxage)
        ref = self._attached_reference.read(maxage)

        self.log.debug('Poti vs. Reference value: %f / %f' %(poti, ref))

        # apply simple scaling
        value = poti / ref

        self.log.debug('uncorrected value: %f' % value)
        result = 0.
        for i, ai in enumerate(self.poly):
            result += ai * (value ** i)
        self.log.debug('final result: %f' % result)

        return result


# heavily based upon old nicm_nok.py, backlash is handled by an axis nowadays
class NOKMotorIPC(CanReference, IPCMotor):
    """Basically a IPCMotor with referencing."""
    parameters = {
        'refpos' : Param('reference position in phys. units', unit='main',
                          type=none_or(float), mandatory=True ),
    }

    parameter_overrides = {
        'zerosteps' : Override(default=500000, mandatory=False),
        'unit'      : Override(default='mm', mandatory=False),
        'backlash'  : Override(type=floatrange(0.0,0.0)), # only 0 is allowed!
        'speed'     : Override(default=10),
        'accel'     : Override(default=10),
        'slope'     : Override(default=2000),
        'confbyte'  : Override(default=48),
        'divider'   : Override(type=intrange(-1,7)),
    }

    def doReference(self):
        bus = self._attached_bus
        bus.send(self.addr, 34) # always go forward (positive)
        bus.send(self.addr, 47, self.speed, 3) # reference with normal speed
        # may need to sleep a little here....
        time.sleep(0.1)
        self.wait()
        self.doSetPosition(self.refpos)


#
# support stuff for the NOK
#

# fancy SequenceItem: if the given device is at a limit switch, move it a little. else do nothing
class SeqMoveOffLimitSwitch(SequenceItem):
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


# fance Sequenceitem: same as SeqDev, but do not go below usermin
class SeqDevMin(SeqDev):
    def __init__(self, dev, target):
        # limit the position to allowed values
        target = clamp(target, dev.usermin, dev.usermax)
        SeqDev.__init__(self, dev, target)


#
# Nicos classes: for NOK's
#


# below code is based upon old nicm_nok.py
class SingleMotorNOK(PseudoNOK, Axis):
    """NOK using a single Axis

    Basically a generic NICOS axis with precision
    """
    parameters = {
        'nok_motor' : Param('Position of the motor for this nok', type=float,
                            settable=False, unit='mm'),
    }

    def doStart(self, target):
        if abs(self.doRead(0) - target) > self.precision:
            Axis.doStart(self, target)

    def doReference(self):
        self._attached_nok_motor.doReference()


class DoubleMotorNOK(SequencerMixin, CanReference, PseudoNOK, HasPrecision, Moveable):
    """NOK using a two Axes

    If backlash is negative, approach form the negative side (default),
    else approach from the positive side.
    If backlash is zero, don't mind and just go to the target.
    """
    attached_devices = {
        'motor_r' : Attach('NOK moving motor, reactor side', Moveable),
        'motor_s' : Attach('NOK moving motor, sample side', Moveable),
    }

    parameters = {
        'nok_motor'         : Param('Position of the motor for this NOK',
                                    type=tupleof(float, float), settable=False,
                                    unit='mm'),
        'inclinationlimits' : Param('allowed range for the positional difference',
                                    type=limits, mandatory=True),
        'backlash'          : Param('backlash correction in phys. units',
                                    type=float, default=0., unit='main'),
    }

    parameter_overrides = {
        'precision'     : Override(type=floatrange(0, 100))
    }

    valuetype = tupleof(float, float)

    @lazy_property
    def _devices(self):
        return self._attached_motor_r, self._attached_motor_s

    def doPreinit(self, mode):
        incmin, incmax = self.inclinationlimits
        if incmin >= incmax:
            raise ConfigurationError(self, 'Inclinationlimits must be specified'
                                            ' as (min, max) tuple with min < max !')

    def doInit(self, mode):
        for dev in self._devices:
            if hasattr(dev, 'backlash') and dev.backlash != 0:
                raise ConfigurationError(self,
                                          'Attached Device %s should not have '
                                          'a non-zero backlash!' % dev)

    def doRead(self, maxage=0):
        return [dev.doRead(maxage) for dev in self._devices]

    def doIsAllowed(self, targets):
        target_r, target_s = targets
        incmin, incmax = self.inclinationlimits

        inclination = target_s - target_r
        if not incmin <= inclination <= incmax:
            return False, 'Inclination %.2f out of limit (%.2f, %.2f)!' % \
                           (inclination, incmin, incmax)

        for dev in self._devices:
            res = dev.isAllowed(target_r)
            if not res[0]:
                return res

        # no problems detected, so it should be safe to go there....
        return True, ''

    def doStart(self, targets):
        """Generates and starts a sequence if none is running.

        The sequence is optimised for negative backlash.
        It will first move both motors to the lowest value of
        (target + backlash, current_position) and then
        to the final target.
        So, inbetween, the NOK should be parallel to the beam.
        """
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')

        # check precision, only move if needed!
        traveldists = [target - dev.doRead(0) for target, dev in zip(targets, self._devices)]
        if max(abs(v) for v in traveldists) <= self.precision:
            return

        devices = self._devices

        # go below lowest interesting point
        minpos = min(self.read() + targets + [t + self.backlash for t in targets])

        # build a referencing sequence
        sequence = []

        # first both go to the lowest point, then to the target
        sequence.append((SeqDev(d, minpos) for d in devices))

        # now go to target
        sequence.append((SeqDev(d, t) for d, t in zip(devices, targets)))

        self._startSequence(sequence)


    def doReference(self):
        """references the NOK in a sophisticated way....

        First we try to reach the lowest point ever needed for referencing,
        then we reference the lower refpoint first, and the higher later.
        After referencing is done, we go to (0, 0).
        """

        if self._seq_is_running():
            raise MoveError(self, 'Cannot reference device, it is still moving!')

        devices = self._devices
        refpos = [d.refpos for d in devices]

        # referencing is easier if device[0].refpos is always lower than device[1].refpos
        if refpos[1] < refpos[0]:
            # wrong order: flip oder of entries
            devices.reverse()
            refpos.reverse()

        # go below lowest interesting point
        minpos = min(self.read() + refpos + [t + self.backlash for t in refpos])

        # build a referencing sequence
        sequence = []

        # go to lowest position first
        sequence.append([SeqDevMin(d, minpos) for d in devices])

        # if one of the motors should have triggered the low-level-switch
        # move them up a little and wait until the movement has finished
        sequence.append([SeqMoveOffLimitSwitch(d, backoffby=self.backlash/4.) for d in devices])

        # ref lowest position, should finish at refpos[0]
        # The move should be first, as the referencing may block!
        sequence.append([SeqDev(devices[1], refpos[0]),
                         SeqMethod(devices[0], 'reference')])

        # ref highest position, should finish at refpos[1]
        sequence.append([SeqDev(devices[0], refpos[1]),
                         SeqMethod(devices[1], 'reference')])

        # fun: move both to 0
        sequence.append([SeqDev(d, 0) for d in devices])

        # GO
        self._startSequence(sequence)
