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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

u"""PUMA specific modifications to NICOS's module for IPC.

(Institut für Physikalische Chemie, Göttingen) hardware classes.
"""

import time

from nicos import session
from nicos.core import Override, Param, intrange, none_or, oneof, status
from nicos.core.constants import SIMULATION
from nicos.core.errors import NicosError, TimeoutError, UsageError
from nicos.core.mixins import HasOffset
from nicos.devices.abstract import CanReference
from nicos.devices.vendor.ipc import Coder as IPCCoder, Motor as IPCMotor
from nicos.pycompat import string_types
from nicos.utils import createThread

DIR_POS = 34
DIR_NEG = 35
SET_CURR_POS = 43
MOVE_REL = 46
WRITE_CONFIG_BYTE = 49

CURR_POS = 130
STATUS = 134


class Coder(IPCCoder):
    """Same as vendor.ipc.Coder but don't write the config byte."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, byte):
        self.log.warning('Config byte can\'t be changed like this.')
        # self._attached_bus.send(self.addr, 154, byte, 3)
        return


class Motor(IPCMotor):
    """Same as vendor.ipc.Motor but don't write the config byte."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        # if self._hwtype == 'single':
        #     self._attached_bus.send(self.addr, WRITE_CONFIG_BYTE, value, 3)
        # else:
        #     raise InvalidValueError(self, 'confbyte not supported by card')
        # self.log.info('parameter change not permanent, use _store() method '
        #               'to write to EEPROM')
        return

    def doWriteSteps(self, value):
        self.log.debug('not setting new steps value: %s', value)
        # self._attached_bus.send(self.addr, SET_CURR_POS, value, 6)
        return


class Motor1(IPCMotor):
    """Same as vendor.ipc.Motor but don't care about limit swtches."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        # if self._hwtype == 'single':
        #     self._attached_bus.send(self.addr, WRITE_CONFIG_BYTE, value, 3)
        # else:
        #     raise InvalidValueError(self, 'confbyte not supported by card')
        # self.log.info('parameter change not permanent, use _store() method '
        #               'to write to EEPROM')
        return

    def doStatus(self, maxage=0):
        state = self._attached_bus.get(self.addr, STATUS)
        st = status.OK

        msg = ''
        # msg += (state & 2) and ', backward' or ', forward'
        # msg += (state & 4) and ', halfsteps' or ', fullsteps'
        if state & 0x10:
            msg += ', inhibit active'
        if state & 0x80:
            msg += ', reference switch active'
        if state & 0x100:
            msg += ', software limit - reached'
        if state & 0x200:
            msg += ', software limit + reached'
        if state & 0x4000 == 0:
            msg += ', external power stage enabled'
        if state & 0x20:
            msg += ', limit switch - active'
        if state & 0x40:
            msg += ', limit switch + active'
        if self._hwtype == 'single':
            msg += (state & 8) and ', relais on' or ', relais off'
            if state & 8:
                # on single cards, if relay is ON, card is supposedly BUSY
                st = status.BUSY
        if state & 0x8000:
            st = status.BUSY
            msg += ', waiting for start/stopdelay'

        # check error states last
        # if state & 0x20 and state & 0x40:
        #     st = status.ERROR
        #     msg = msg.replace('limit switch - active, limit switch + active '
        #                       'EMERGENCY STOP pressed or both limit switches'
        #                       ' broken')
        # if state & 0x400:
        #     st = status.ERROR
        #     msg += ', device overheated'
        # if state & 0x800:
        #     st = status.ERROR
        #     msg += ', motor undervoltage'
        # if state & 0x1000:
        #     st = status.ERROR
        #     msg += ', motor not connected or leads broken'
        # if state & 0x2000:
        #     st = status.ERROR
        #     msg += ', hardware failure or device not reset after power-on'

        # if it's moving, it's not in error state! (except if the emergency
        # stop is active)
        if state & 1 and (state & 0x60 != 0x60):
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s', st, msg[2:])
        return st, msg[2:]


class ReferenceMotor(CanReference, Motor):
    """IPC stepper card motor with reference capability."""

    parameters = {
        'refswitch': Param('Type of the reference switch',
                           type=oneof('high', 'low', 'ref'),
                           mandatory=True, settable=False),
        'maxtries': Param('Number of tries to reach the target', type=int,
                          default=3, settable=True),
        'parkpos': Param('Position to move after reaching reference switch',
                         type=none_or(float), unit='main', settable=False,
                         default=None),
        'refpos': Param('Number of steps at reference position',
                        type=intrange(0, 999999), settable=False,
                        default=500000),
        'refspeed': Param('Speed value during the reference move',
                          type=intrange(0, 255), settable=False),
        'refstep': Param('Steps to move away from reference switch',
                         type=intrange(0, 999999), settable=False,
                         default=2000),
        'refmove': Param('Steps to move to the reference switch',
                         type=intrange(0, 10000), settable=False,
                         default=100),
        'refdirection': Param('Direction of the reference move'
                              'to "lower" or "upper" step values',
                              type=oneof('lower', 'upper'), settable=False,
                              default='lower'),
    }

    parameters_override = {
        'timeout': Override(default=600.),
    }

    def doInit(self, mode):
        Motor.doInit(self, mode)
        self._stoprequest = 0
        self._refcontrol = None
        if mode != SIMULATION:
            try:
                current_val = self.doReadSpeed()
                if self.speed != current_val:
                    self.doWriteSpeed(self.speed)
            except NicosError:
                self.log.warning("Could not write 'speed' value")
            try:
                current_val = self.doReadAccel()
                if self.accel != current_val:
                    self.doWriteAccel(self.accel)
            except NicosError:
                self.log.warning("Could not write 'accel' value")
            try:
                current_val = self.doReadMicrostep()
                if self.microstep != current_val:
                    self.doWriteMicrostep(self.microstep)
            except NicosError:
                self.log.warning("Could not write 'microstep' value")
        self._lasterror = None

    def doStop(self):
        self._stoprequest = 1
        Motor.doStop(self)
        if self._refcontrol and self._refcontrol.isAlive():
            self._refcontrol.join()
        self._refcontrol = None

    def doStatus(self, maxage=0):
        """Return the status of the motor controller."""
        if self._mode == SIMULATION:
            return (status.OK, '')
        elif self._refcontrol and self._refcontrol.isAlive():
            return (status.BUSY, 'referencing')
        return Motor.doStatus(self, maxage)

    def doReference(self, *args):
        refswitch = args[0] if args and isinstance(args[0], string_types) \
            else None
        if self.doStatus()[0] == status.BUSY:
            self.stop()
            self.wait()

        # The sixfold and triple cards will be reset as whole card, so values
        # of all channels will reset !!!
        # self.reset()
        # self.wait()

        if self.doStatus()[0] == status.OK:
            if self._refcontrol and self._refcontrol.isAlive():
                self._refcontrol.join()
            self._refcontrol = None

            if self._refcontrol is None:
                threadname = 'referencing %s' % self
                self._refcontrol = createThread(threadname, self._reference,
                                                args=(refswitch,))
                session.delay(0.2)
        else:
            raise NicosError(self, 'in error or busy state')

    def doWriteSteps(self, value):
        self.log.debug('setting new steps value: %s', value)
        self._attached_bus.send(self.addr, SET_CURR_POS, value, 6)
        ret = self._attached_bus.get(self.addr, CURR_POS)
        self.log.debug('set new steps value: %s', ret)
        return ret

    def _start(self, target):
        target = self._tosteps(target)
        pos = self._tosteps(self.read(0))
        self.log.debug('target is %d steps, pos is %d steps', target, pos)
        diff = target - pos
        if diff:
            self._attached_bus.send(self.addr,
                                    DIR_NEG if diff < 0 else DIR_POS)
            self._attached_bus.send(self.addr, MOVE_REL, abs(diff), 6)
            session.delay(0.1)
            # hw_wait will not work here, since the status of the device is
            # always busy, but only the state of the motor is important
            while Motor.doStatus(self, 0)[0] == status.BUSY and \
                    not self._stoprequest:
                session.delay(self._base_loop_delay)
            # motor must be stopped, the hardware will go again if any of the
            # limit switches is released again, this leads to unpredictable
            # results!
            Motor.doStop(self)

    def _reference(self, refswitch=None):
        """Drive motor to reference switch."""
        self.log.debug('referencing: %s', refswitch)

        # init referencing
        self._stoprequest = 0
        # if reference switch is explicitly given only drive to given limit
        # switch
        fullref = refswitch is None
        if refswitch is None:
            refswitch = self.refswitch
        if refswitch == self.refswitch:
            refdirection = self.refdirection
        else:  # refdirection must be opposite from configured
            if self.refdirection == 'upper':
                refdirection = 'lower'
            else:
                refdirection = 'upper'
            self.log.debug('switch %s, direction %s, %s', refswitch,
                           self.refdirection, refdirection)
        try:
            _min, _max, motspeed = self.min, self.max, self.speed
            self._resetlimits()
            self._drive_to_limit_switch(refswitch, refdirection)
            if fullref:
                if self.isAtReference():
                    self._move_away_from_reference(refswitch, refdirection)
                self._move_until_referenced(time.time())
                if self.isAtReference():
                    if self.parkpos is not None:
                        self._start(self.parkpos)
                if self._stoprequest == 1:
                    raise NicosError(self, 'reference stopped by user')
        except TimeoutError as e:
            self.log.error('%s occured during referencing', e)
        except NicosError as e:
            self.log.error('%s: occured during referencing', e)
        except Exception as e:
            self.log.error('%s: occured during referencing', e)
        finally:
            self.log.debug('stoprequest: %d', self._stoprequest)
            self.speed = motspeed
            self.min = _min
            self.max = _max
            if fullref:
                try:
                    temp = self.read(0)
                    self.log.info('new position of %s is now %.3f %s',
                                  self.name, temp, self.unit)
                    if self.abslimits[0] <= temp <= self.abslimits[1]:
                        self._resetlimits()
                    else:
                        self.log.warn('in _referencing limits not restored '
                                      'after positioning')
                except NicosError as e:
                    self.log.warn('error catched in finally positioning %s', e)

    def _drive_to_limit_switch(self, switch, direction):
        self.log.debug('driving to %r switch towards %r', switch, direction)
        if not self.isAtReference(switch):
            self.log.debug('in _drive_to_limitswitch checkrefswitch')
            self._drive_to_reference(self.refspeed, switch, direction)
            if not self.isAtReference(switch):
                if self._stoprequest == 1:
                    raise NicosError(self, 'limitswitch drive stopped by user')

    def isAtReference(self, refswitch=None):
        """Check whether configured reference switch is active."""
        self.log.debug('in isAtReference function')
        if refswitch is None:
            refswitch = self.refswitch
        return (refswitch == 'high' and self._isAtHighlimit()) or \
               (refswitch == 'low' and self._isAtLowlimit()) or \
               (refswitch == 'ref' and self._isAtReferenceSwitch())

    def _read_status(self):
        return self._attached_bus.get(self.addr, STATUS)

    def _isAtHighlimit(self):
        val = self._read_status()
        if self._hwtype == 'sixfold':
            if self.firmware < 63:
                return bool(val & 0x20)
        return bool(val & 0x40)

    def _isAtLowlimit(self):
        val = self._read_status()
        if self._hwtype == 'sixfold':
            if self.firmware < 63:
                return bool(val & 0x40)
        return bool(val & 0x20)

    def _isAtReferenceSwitch(self):
        val = self._read_status()
        return bool(val & 0x80)

    def _setrefcounter(self):
        self.log.debug('in setrefcounter')
        if not self.isAtReference():
            raise UsageError('cannot set reference counter, not at reference '
                             'point')
        self.steps = self.refpos

    def _resetlimits(self):
        alim = self.abslimits
        if isinstance(self, HasOffset):
            newlim = (alim[0] - self.offset, alim[1] - self.offset)
        else:
            newlim = alim
        if self.userlimits != newlim:
            self.userlimits = newlim

    def _drive_to_reference(self, refspeed, refswitch, refdirection):
        self.log.debug('reference: switch %s, direction %s', refswitch,
                       refdirection)
        if refswitch in ['high', 'low']:
            if refdirection == 'lower':
                if self.slope > 0:
                    stop, start = self._hw_limits
                else:
                    start, stop = self._hw_limits
            else:
                if self.slope > 0:
                    start, stop = self._hw_limits
                else:
                    stop, start = self._hw_limits
            # if start > stop:
            #     start, stop = stop, start
            self.setPosition(start)
            self.log.debug('move to %f from %f', stop, start)
            self._start(stop)
            self.log.debug('finished at %f', self.read(0))
            if self._stoprequest:
                raise NicosError(self, 'reference stopped by user')

    def _move_away_from_reference(self, refswitch, refdirection):
        self.log.debug('%s limit switch active', refswitch)
        self.steps = self.refpos
        d = abs(self.refstep / self.slope)
        if refdirection == 'lower':
            d = -d
        self.log.debug('move away from reference switch %f', d)
        self._start(self.read(0) - d)
        if self._stoprequest:
            raise NicosError(self, 'reference stopped by user')

    def _move_until_referenced(self, starttime):
        # calculate the step size for each reference move
        d = abs(self.refmove / self.slope)
        if self.refdirection == 'lower':
            d = -d
        while not self.isAtReference():
            p = self.read(0)
            t = p + d
            self.log.debug('move to %s limit switch %r -> %r',
                           self.refswitch, p, t)
            self._start(t)
            if self._stoprequest:
                raise NicosError(self, 'reference stopped by user')
            if time.time() - starttime > self.timeout:
                raise TimeoutError(self, 'timeout occured during reference '
                                   'drive')
        self._setrefcounter()

    @property
    def _hw_limits(self):
        return (self._fromsteps(self.min), self._fromsteps(self.max))
