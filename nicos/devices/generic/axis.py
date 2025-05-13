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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS axis classes."""

from time import sleep

from nicos.core import Attach, ConfigurationError, HasOffset, MoveError, \
    NicosError, Override, Param, PositionError, floatrange, status, \
    waitForCompletion
from nicos.core.constants import MASTER, SIMULATION
from nicos.devices.abstract import Axis as AbstractAxis, CanReference, Coder, \
    Motor
from nicos.utils import createThread


class Axis(CanReference, AbstractAxis):
    """Axis implemented in Python, with NICOS devices for motor and coders."""

    attached_devices = {
        'motor': Attach('Axis motor device', Motor),
        'coder': Attach('Main axis encoder device', Coder, optional=True),
        'obs':   Attach('Auxiliary encoders used to verify position', Coder,
                        optional=True, multiple=True),
    }

    parameter_overrides = {
        'precision': Override(mandatory=True,),
        # these are not mandatory for the axis: the motor should have them
        # defined anyway, and by default they are correct for the axis as well
        'abslimits': Override(mandatory=False, volatile=True),
        'userlimits': Override(volatile=True),
    }

    parameters = {
        'speed':       Param('Motor speed', unit='main/s', volatile=True,
                             settable=True),
        'jitter':      Param('Amount of position jitter allowed', unit='main',
                             type=floatrange(0.0, 10.0), settable=True),
        'obsreadings': Param('Number of observer readings to average over '
                             'when determining current position', type=int,
                             default=100, settable=True),
    }

    hardware_access = False

    errorstates = {}

    def doInit(self, mode):
        if self._attached_coder is None:
            self.log.debug('using the motor as coder too as no coder was '
                           'specified in the setup file')
        # Check that motor and coder have the same unit
        elif self._attached_coder.unit != self._attached_motor.unit:
            raise ConfigurationError(self, 'different units for motor and '
                                     'coder (%s vs %s)' %
                                     (self._attached_motor.unit,
                                      self._attached_coder.unit)
                                     )
        # Check that all observers have the same unit as the motor
        for ob in self._attached_obs:
            if self._attached_motor.unit != ob.unit:
                raise ConfigurationError(self, 'different units for motor '
                                         'and observer %s' % ob)

        # Check for userlimits in configuration
        if 'userlimits' in self._config:
            self.log.warning('userlimits in setup file ignored; configure '
                             'them on the motor device if really needed')
        if getattr(self._attached_motor, 'offset', 0) != 0:
            self.log.warning('motor has a nonzero offset; this will cause '
                             'general confusion and problems with userlimits')

        self._hascoder = self._attached_coder is not None and \
            self._attached_motor != self._attached_coder
        self._errorstate = None
        self._posthread = None
        self._stoprequest = 0
        self._maxdiff = self.dragerror if self._hascoder else 0.0

        if mode == MASTER and self._hascoder and \
           self.motor.status()[0] != status.BUSY and \
           abs(self.motor.read() - self.coder.read()) > self.precision:
            self.log.warning('motor and encoder have different positions '
                             '(%s vs. %s), setting motor position to coder '
                             'position',
                             self.motor.format(self.motor.read()),
                             self.coder.format(self.coder.read()))
            self._updateMotorPosition()

    def _updateMotorPosition(self):
        self.motor.setPosition(self._getReading())

    # legacy properties for users, DO NOT USE lazy_property here!

    @property
    def motor(self):
        return self._attached_motor

    @property
    def coder(self):
        return self._attached_coder

    def doReadUnit(self):
        return self._attached_motor.unit

    def doReadAbslimits(self):
        mot_amin, mot_amax = self._attached_motor.abslimits
        # if abslimits are configured, use them, but they can only restrict,
        # not widen, the motor's abslimits
        if 'abslimits' in self._config:
            amin, amax = self._config['abslimits']
            if amin < mot_amin - abs(mot_amin * 1e-12):
                raise ConfigurationError(self, 'abslimits: min (%s) below '
                                         "motor's min (%s)" % (amin, mot_amin))
            if amax > mot_amax + abs(mot_amax * 1e-12):
                raise ConfigurationError(self, 'abslimits: max (%s) above '
                                         "motor's max (%s)" % (amax, mot_amax))
        else:
            amin, amax = mot_amin, mot_amax
        return amin, amax

    def doReadUserlimits(self):
        # userlimits are always taken from the motor to avoid multiple
        # conflicting limit settings
        umin, umax = self._attached_motor.userlimits
        return umin - self.offset, umax - self.offset

    def doWriteUserlimits(self, value):
        # pylint: disable=assignment-from-none
        rval = AbstractAxis.doWriteUserlimits(self, value)
        limits = rval if rval else value
        # if the offset is currently changing, we need to use _new_offset
        self._attached_motor.userlimits = (
            limits[0] + getattr(self, '_new_offset', self.offset),
            limits[1] + getattr(self, '_new_offset', self.offset)
        )

    def doIsAllowed(self, target):
        # do limit check here already instead of in the thread
        ok, why = self._attached_motor.isAllowed(target + self.offset)
        if not ok:
            return ok, 'motor cannot move there (offset = %.3f): %s' % (
                self.offset, why)
        return True, ''

    def doStart(self, target):
        """Starts the movement of the axis to target."""
        if self._mode == SIMULATION:
            if not self._checkTargetPosition(self.read(0), target,
                                             error=False):
                self._attached_motor.start(target + self.offset)
                if self._hascoder:
                    self._attached_coder._sim_setValue(target + self.offset)
            return

        if self.status(0)[0] == status.BUSY:
            self.log.debug('need to stop axis first')
            self.stop()
            waitForCompletion(self, ignore_errors=True)

        self._startPositioningThread(target)

    def _startPositioningThread(self, target):
        if self._posthread:
            if self._posthread.is_alive():
                self._posthread.join()
            self._posthread = None

        self._stoprequest = 0
        self._errorstate = None
        if self._checkTargetPosition(self.read(0), target, error=False):
            self.log.debug('not moving, already at %.4f within precision',
                           target)
            return

        self._target = target
        self._posthread = createThread('positioning thread %s' % self,
                                       self.__positioningThread)

    def _getWaiters(self):
        if self._mode == SIMULATION:
            return [self._attached_motor]
        # Except for dry runs, the Axis does its own status control, there is
        # no need to wait for the motor as well.
        return []

    def doStatus(self, maxage=0):
        """Return the status of the motor controller."""
        if self._mode == SIMULATION:
            return (status.OK, '')
        elif self._posthread and self._posthread.is_alive():
            return (status.BUSY, 'moving')
        elif self._errorstate:
            return (status.ERROR, str(self._errorstate))
        else:
            self.log.debug('no motion thread, using motor status')
            return self._attached_motor.status(maxage)

    def doRead(self, maxage=0):
        """Return the current position from coder controller."""
        return (self._attached_coder if self._hascoder else
                self._attached_motor).read(maxage) - self.offset

    def doPoll(self, i, maxage):
        self._attached_motor.poll(i, maxage)
        if self._hascoder:
            self._attached_coder.poll(i, maxage)
        for dev in self._attached_obs:
            dev.poll(i, maxage)

    def _getReading(self):
        """Find a good value from the observers.

        Taking into account that they usually have lower resolution, so we
        have to average of a few readings to get a (more) precise value.
        """
        # if coder != motor -> use coder (its more precise!)
        # if no observers, rely on coder (even if its == motor)
        if self._hascoder:
            # read the coder
            return self._attached_coder.read(0)
        if self._attached_obs:
            obs = self._attached_obs
            rounds = self.obsreadings
            pos = sum(o.doRead() for _ in range(rounds) for o in obs)
            return pos / float(rounds * len(obs))
        return self._attached_motor.read(0)

    def doReset(self):
        """Reset the motor/coder controller."""
        self._attached_motor.reset()
        if self._hascoder:
            self._attached_coder.reset()
        for obs in self._attached_obs:
            obs.reset()
        if self.status(0)[0] != status.BUSY:
            self._errorstate = None
        self._updateMotorPosition()
        if not self._hascoder:
            self.log.info('reset done; use %s.reference() to do a reference '
                          'drive', self)

    def doReference(self):
        """Do a reference drive, if the motor supports it."""
        if self._hascoder:
            self.log.error('this is an encoded axis, '
                           'referencing makes no sense')
            return
        motor = self._attached_motor
        if isinstance(motor, CanReference):
            return motor.reference()
        else:
            self.log.error('motor %s does not have a reference routine',
                           motor)

    def doStop(self):
        """Stops the movement of the motor."""
        self._stoprequest = 1
        # send a stop in case the motor was started via the attached motor
        # device, or externally.
        self._attached_motor.stop()

    def doFinish(self):
        if self._errorstate:
            errorstate = self._errorstate
            self._errorstate = None
            raise errorstate  # pylint: disable=raising-bad-type

    def doTime(self, old_value, target):
        if hasattr(self._attached_motor, 'doTime'):
            return self._attached_motor.doTime(old_value, target)
        return abs(target - old_value) / self.speed if self.speed != 0 else 0.

    def doWriteDragerror(self, value):
        if not self._hascoder:
            if value != 0:
                self.log.warning('setting a non-zero value for drag error only '
                                 'works if a coder was specified in the setup, '
                                 'which is different from the motor')
            return 0.0
        else:
            self._maxdiff = value

    def doWriteSpeed(self, value):
        self._attached_motor.speed = value

    def doReadSpeed(self):
        return self._attached_motor.speed

    def doWriteOffset(self, value):
        """Called on adjust(), overridden to forbid adjusting while moving."""
        self._new_offset = value
        if self.status(0)[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                             'command and try it again')
        if self._errorstate:
            raise self._errorstate  # pylint: disable=raising-bad-type
        del self._new_offset
        HasOffset.doWriteOffset(self, value)

    def _preMoveAction(self):
        """This method will be called before the motor will be moved.
        It should be overwritten in derived classes for special actions.

        To abort the move, raise an exception from this method.
        """

    def _postMoveAction(self):
        """This method will be called after the axis reached the position or
        will be stopped.
        It should be overwritten in derived classes for special actions.

        To signal an error, raise an exception from this method.
        """

    def _duringMoveAction(self, position):
        """This method will be called during every cycle in positioning thread.
        It should be used to do some special actions like changing shielding
        blocks, checking for air pressure etc.  It should be overwritten in
        derived classes.

        To abort the move, raise an exception from this method.
        """

    def _checkDragerror(self):
        """Check if a "drag error" occurred.

        The values of motor and coder deviate too much.  This indicates that
        the movement is blocked.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        if self._maxdiff <= 0:
            return True
        diff = abs(self._attached_motor.read() - self._attached_coder.read())
        self.log.debug('motor/coder diff: %s', diff)
        if diff > self._maxdiff:
            self._errorstate = MoveError(self, 'drag error (primary coder): '
                                         'difference %.4g, maximum %.4g' %
                                         (diff, self._maxdiff))
            return False
        for obs in self._attached_obs:
            diff = abs(self._attached_motor.read() - obs.read())
            if diff > self._maxdiff:
                self._errorstate = PositionError(
                    self, 'drag error (%s): difference %.4g, maximum %.4g' %
                    (obs.name, diff, self._maxdiff))
                return False
        return True

    def _checkMoveToTarget(self, target, pos):
        """Check that the axis actually moves towards the target position.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        delta_last = self._lastdiff
        delta_curr = abs(pos - target)
        self.log.debug('position delta: %s, was %s', delta_curr, delta_last)
        # at the end of the move, the motor can slightly overshoot during
        # movement we also allow for small jitter, since air pads usually wiggle
        # a little resulting in non-monotonic movement!
        ok = (delta_last >= (delta_curr - self.jitter)) or \
            delta_curr < self.precision
        # since we allow to move away a little, we want to remember the
        # smallest distance so far so that we can detect a slow crawl away from
        # the target which we would otherwise miss
        self._lastdiff = min(delta_last, delta_curr)
        if not ok:
            self._errorstate = MoveError(self, 'not moving to target: '
                                         'last delta %.4g, current delta %.4g'
                                         % (delta_last, delta_curr))
            return False
        return True

    def _checkTargetPosition(self, target, pos, error=True):
        """Check if the axis is at the target position.

        This method returns False if not arrived at target, or True otherwise.
        """
        diff = abs(pos - target)
        prec = self.precision
        if (0 < prec <= diff) or (prec == 0 and diff):
            msg = 'precision error: difference %.4g, precision %.4g' % \
                  (diff, self.precision)
            if error:
                self._errorstate = MoveError(msg)
            else:
                self.log.debug(msg)
            return False
        maxdiff = self.dragerror
        for obs in self._attached_obs:
            diff = abs(target - (obs.read() - self.offset))
            if 0 < maxdiff < diff:
                msg = 'precision error (%s): difference %.4g, maximum %.4g' % \
                      (obs, diff, maxdiff)
                if error:
                    self._errorstate = PositionError(msg)
                else:
                    self.log.debug(msg)
                return False
        return True

    def _setErrorState(self, cls, text):
        self._errorstate = cls(self, text)
        self.log.error(text)
        return False

    def __positioningThread(self):
        try:
            self._preMoveAction()
        except Exception as err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' %
                                err)
            return
        target = self._target
        self._errorstate = None
        positions = [(target, True)]
        if self.backlash:
            backlash = self.backlash
            lastpos = self.read(0)
            # make sure not to move twice if coming from the side in the
            # direction of the backlash
            backlashpos = target + backlash
            if (backlash > 0 and lastpos < target) or \
               (backlash < 0 and lastpos > target):
                # if backlash position is not allowed, just don't use it
                if self.isAllowed(backlashpos)[0]:
                    positions.insert(0, (backlashpos, False))
                else:
                    # at least try to move to limit
                    if backlashpos > target:
                        limit = self.userlimits[1]
                    else:
                        limit = self.userlimits[0]
                    if self.isAllowed(limit)[0]:
                        positions.insert(0, (limit, False))
                    else:
                        self.log.debug('cannot move to backlash position')
        for (pos, precise) in positions:
            try:
                self.__positioning(pos, precise)
            except Exception as err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                break
        try:
            self._postMoveAction()
        except Exception as err:
            self._setErrorState(MoveError,
                                'error in post-move action: %s' % err)

    def __positioning(self, target, precise=True):
        self.log.debug('start positioning, target is %s', target)
        moving = False
        offset = self.offset
        tries = self.maxtries

        # enforce initial good agreement between motor and coder
        if not self._checkDragerror():
            self._updateMotorPosition()
            self._errorstate = None

        self._lastdiff = abs(target - self.read(0))
        self._attached_motor.start(target + offset)
        moving = True
        stoptries = 0

        while moving:
            if self._stoprequest == 1:
                self.log.debug('stopping motor')
                self._attached_motor.stop()
                self._stoprequest = 2
                stoptries = 10
                continue
            sleep(self.loopdelay)
            # poll accurate current values and status of child devices so that
            # we can use read() and status() subsequently
            # always poll motor first!
            mstatus, mstatusinfo = self._attached_motor.status(0)
            _status, pos = self.poll()
            if mstatus != status.BUSY:
                # motor stopped; check why
                if self._stoprequest == 1:
                    self.log.debug('stop requested')
                    # will stop on next loop
                elif self._stoprequest == 2:
                    self.log.debug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif not precise and not self._errorstate:
                    self.log.debug('motor stopped and precise positioning '
                                   'not requested')
                    moving = False
                elif self._checkTargetPosition(target, pos,
                                               error=not self._errorstate):
                    self.log.debug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif mstatus == status.ERROR:
                    self.log.debug('motor in error status (%s), trying reset',
                                   mstatusinfo)
                    # motor in error state -> try resetting
                    newstatus = self._attached_motor.reset()
                    # if that failed, stop immediately
                    if newstatus[0] == status.ERROR:
                        moving = False
                        self._setErrorState(MoveError, 'motor in error state: '
                                            '%s' % newstatus[1])
                elif tries > 0:
                    if tries == 1:
                        self.log.warning('last try: %s', self._errorstate)
                    else:
                        self.log.debug('target not reached, retrying: %s',
                                       self._errorstate)
                    self._errorstate = None
                    # target not reached, get the current position, set the
                    # motor to this position and restart it. _getReading is the
                    # 'real' value, may ask the coder again (so could slow
                    # down!)
                    self._updateMotorPosition()
                    self._attached_motor.start(target + self.offset)
                    tries -= 1
                else:
                    moving = False
                    self._setErrorState(MoveError, 'target not reached after '
                                        '%d tries: %s' % (self.maxtries,
                                                          self._errorstate))
            elif not self._checkMoveToTarget(target, pos):
                self.log.debug('stopping motor because not moving to target')
                self._attached_motor.stop()
                # should now go into next try
            elif not self._checkDragerror():
                self.log.debug('stopping motor due to drag error')
                self._attached_motor.stop()
                # should now go into next try
            elif self._stoprequest == 0:
                try:
                    self._duringMoveAction(pos)
                except Exception as err:
                    self._setErrorState(MoveError, 'error in during-move '
                                        'action: %s' % err)
                    self._stoprequest = 1
            elif self._stoprequest == 2:
                # motor should stop, but does not want to?
                stoptries -= 1
                if stoptries < 0:
                    self._setErrorState(MoveError, 'motor did not stop after '
                                        'stop request, aborting')
                    moving = False
        self.log.debug('inner positioning loop finished')
