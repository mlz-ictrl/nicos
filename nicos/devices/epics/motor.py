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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import time

import numpy as np

from nicos import session
from nicos.core import Override, Param, UsageError, oneof, pvname, \
    status
from nicos.core.constants import MASTER
from nicos.core.mixins import CanDisable, HasOffset
from nicos.core.params import anytype, limits
from nicos.devices.abstract import CanReference, Motor
from nicos.devices.epics import EpicsAnalogMoveable
from nicos.devices.epics.status import SEVERITY_TO_STATUS

class EpicsMotor(CanReference, HasOffset, CanDisable, EpicsAnalogMoveable, Motor):
    """
    This device exposes some of the functionality provided by the
    `EPICS motor record <https://epics.anl.gov/bcda/synApps/motor/motorRecord.html>`_.

    The PV names for the fields of the record (readback, speed, etc.)
    are derived by combining the motorpv-parameter with the predefined field
    names.

    The reseterrorpv can be provided optionally in case the supports a reset-
    mechanism that tries to recover from certain errors. If present, these are
    used when calling the reset()-method.

    Another optional PV is the errormsgpv, which contains an error message that
    may originate from the motor controller or the IOC. If it is present,
    doStatus uses it for some of the status messages.

    The EPICS motor record includes an
    `offset field <https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_calib>`_,
    that, when changed, automatically updates the
    `limits <https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_limit>`_,
    `target <https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_drive>`_,
    and `current position <https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_status>`_
    fields of the same record.  To keep the corresponding parameters in NICOS
    in sync, each are marked volatile and read directly from EPICS.
    Unfortunately, however, EPICS applies it's offset in the opposite direction,
    for which reason this device has both a normal NICOS `offset` and the
    parameter `epics_offset`, with `epics_offset` reflecting the value within
    EPICS and `offset` being its inverse.

    Furthermore, NICOS assumes that the absolute limits don't already have the
    offset applied.  To this end there is both an `epics_abslimits` parameter
    that reflects the limits in EPICS (i.e. with offset applied) and `abslimits`
    that follows the NICOS convention.  Together this avoids frustrations when
    reloading values from the cache, the code for which assumes that the
    offsets and limits follow a NICOS specific convention.
    """
    parameters = {
        'motorpv':
            Param('Name of the motor record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'errormsgpv':
            Param('Optional PV with error message.',
                  type=pvname,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'reseterrorpv':
            Param('Optional PV with error reset switch.',
                  type=pvname,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'reference_direction':
            Param('Reference run direction.',
                  type=oneof('forward', 'reverse'),
                  default='forward',
                  settable=False,
                  userparam=False,
                  mandatory=False),
        'direction':
            Param('Run direction',
                  type=oneof('forward', 'reverse'),
                  settable=True,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        'epics_abslimits':
            Param('Epics HLM and LLM fields',
                  type=limits,
                  category='limits',
                  settable=False,
                  internal=True,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        'epics_offset':
            Param('Epics OFF field',
                  category='offsets',
                  settable=False,
                  internal=True,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        'speedlimits':
            Param('Epics VBAS and VMAX fields',
                  type=limits,
                  category='limits',
                  settable=False,
                  internal=True,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        'position_deadband':
            Param('Only move if the distance between target and current ' \
                  'position is larger than this value',
                  type=float,
                  category='precisions',
                  settable=False,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        'startdelay':
            Param('Maximum time in seconds before starting a movement is ' \
                  'considered as failed',
                  type=float,
                  category='general',
                  settable=False,
                  mandatory=False,
                  userparam=True,
                  default=1),
        'cached_status':
            Param('Last motor status',
                  type=anytype,
                  category='general',
                  settable=True,
                  mandatory=False,
                  internal=True,
                  default=(status.OK, '')),
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),

        # speed, limits offset and target may change from outside,
        # so can't rely on cache
        'speed': Override(volatile=True),
        'offset': Override(volatile=True, chatty=False),
        'abslimits': Override(volatile=True),
        'precision': Override(settable=False, mandatory=False, volatile=True),
    }

    # Holds the time at which the last movement command was given.
    _start_time = None

    # Maximum time the doReset function waits until it assumes the reset command
    # has been processed
    _reset_delay = 10

    # Maximum time the doStop function waits until it assumes the stop command
    # has been processed
    _stop_delay = 10

    # Default error message for motor record issues when no errormsgpv is
    # provided
    _default_errormsg = 'Hardware error. Please call the support.'

    # Fields of the motor record for which an interaction via Channel Access
    # is required.
    _record_fields = {
        'readpv': 'RBV',
        'writepv': 'VAL',
        'stop': 'STOP',
        'donemoving': 'DMOV',
        'moving': 'MOVN',
        'miss': 'MISS',
        'homeforward': 'HOMF',
        'homereverse': 'HOMR',
        'direction': 'DIR',
        'speed': 'VELO',
        'basespeed': 'VBAS',
        'maxspeed': 'VMAX',
        'offset': 'OFF',
        'highlimit': 'HLM',
        'lowlimit': 'LLM',
        'softlimit': 'LVIO',
        'lowlimitswitch': 'LLS',
        'highlimitswitch': 'HLS',
        'resolution': 'MRES',
        'enable': 'CNEN',
        'set': 'SET',
        'foff': 'FOFF',
        'status': 'MSTA',
        'alarm_status': 'STAT',
        'alarm_severity': 'SEVR',
        'position_deadband': 'SPDB',
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in motor record.

        :return: List of PV aliases.
        """
        pvs = set(self._record_fields)

        if self.errormsgpv:
            pvs.add('errormsgpv')

        if self.reseterrorpv:
            pvs.add('reseterrorpv')

        return pvs

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the motorpv parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        motor_field = self._record_fields.get(pvparam)

        if motor_field is not None:
            return '.'.join((self.motorpv, motor_field))

        return getattr(self, pvparam)

    def doPreinit(self, mode):
        EpicsAnalogMoveable.doPreinit(self, mode)

        if mode == MASTER:
            # As the absolute limits and offset are managed by Epics, may be
            # the case, that these change while Nicos is not running, meaning
            # that the user limits are no longer within the absolute limits. As
            # a result, it is no longer possible for devices of this type to be
            # created, due to exceptions thrown by the `_checkLimits` method in
            # the `HasLimits` mixin. For this reason, we override the user
            # limits during startup if they are outside the absolute limits.

            absmin = self._get_pv('lowlimit')
            absmax = self._get_pv('highlimit')
            epicsoffset = self._get_pv('offset')

            default_userlimits = (absmin - epicsoffset, absmax - epicsoffset)

            userlimits = self._cache.get(self._name, "userlimits",
                                         default=(absmin - epicsoffset, absmax - epicsoffset))

            if userlimits == (0., 0.):
                userlimits = default_userlimits

            # in HasLimits we have _checkLimits(self, limits)
            # umin < amin - abs(amin * 1e-12)
            # and
            # umax > amax + abs(amax * 1e-12)
            # So perhaps this is a little too large a change
            usermin, usermax = userlimits
            usermin = max(absmin - epicsoffset + abs(absmin * 1e-10), usermin)
            usermax = min(absmax - epicsoffset - abs(absmax * 1e-10), usermax)

            if userlimits != (usermin, usermax):
                # if the change is major (> 10 %), inform the user, otherwise
                # just log it in debug. The denominator is the delta between
                # the calculated "new" userlimits.
                denom = usermax - usermin
                if (abs((userlimits[0] - usermin) / denom) > 0.1 or
                    abs((userlimits[1] - usermax) / denom) > 0.1):
                    logfn = self.log.warning
                else:
                    logfn = self.log.debug
                logfn('User limits are outside absolute limits %s - was: %s, now: %s',
                                (absmin, absmax), userlimits, (usermin, usermax))
                self._cache.put(self._name, "userlimits", (usermin, usermax))

    def doReadSpeed(self):
        return self._get_pv('speed')

    def doReadPrecision(self):
        return self._get_pv('resolution')

    def doReadPosition_Deadband(self):
        return self._get_pv('position_deadband')

    def doWriteSpeed(self, value):
        basespeed, maxspeed = self.speedlimits
        if value < basespeed:
            self.log.warning(
                'Selected speed %s is lower than the low limit %s. '
                'Using low limit %s instead.', value, basespeed, basespeed)
            value = basespeed

        elif value > maxspeed:
            self.log.warning(
                'Selected speed %s is higher than the high limit %s. '
                'Using high limit %s instead.', value, maxspeed, maxspeed)
            value = maxspeed

        # Before proceeding, we want to make sure that the PV has actually been
        # changed.
        self._put_pv_readback_checked('speed', value,
                                      timeout=self.epicstimeout,
                                      abstol=self.precision)
        return value

    def doReadEpics_Offset(self):
        return self._get_pv('offset')

    def doReadOffset(self):
        return -self.epics_offset

    def doWriteOffset(self, value):
        # In EPICS, the offset is defined in following way:
        # USERval = HARDval + offset

        if self.offset != value:
            old_offset = self.offset
            diff = value - self.offset

            # Adjust the limits before the EPICS absolute limits have been updated.
            self._adjustLimitsToOffset(value, diff)

            # Set the offset in the motor record, which in turn adjusts the
            # absolute limits
            self._put_pv_readback_checked('offset', -value,
                                          timeout=self.epicstimeout,
                                          abstol=self.precision)

            # Force a cache update of volatile parameters
            self.target   # pylint: disable=pointless-statement
            self.read(0)  # pylint: disable=pointless-statement

            session.elogEvent('offset', (str(self), old_offset, value))

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        self._start_time = time.time()
        # Needs to be checked because self.doReadTarget is called immediately
        # afterwards when doing a move-and-wait.
        self._put_pv_readback_checked('writepv', value,
                                        timeout=self.epicstimeout,
                                        abstol=self.precision)

    def doReadTarget(self):
        return self._get_pv('writepv')

    def doIsAtTarget(self, pos, target):
        if self._sim_intercept or target is None:
            return True

        # A motor can have a deadband which is larger than the precision. Hence,
        # the doIsAtTarget method is used in a modified form here
        return (self._get_pv('miss') == 0 and
                abs(target - pos) <= max(self.precision, self.position_deadband))

    def doWritePrecision(self, value):
        raise UsageError('Precision is read directly from the .MRES field of '
                         'the motor record and therefore cannot be set')

    def _log_status_error(self, stat, msg_txt):
        """
        Logging the status retrieved from _get_status_message is factored out
        into its own method so it can be overloaded in subclasses.
        """
        if stat == status.WARN:
            self.log.warning('%s', msg_txt)
        elif stat == status.ERROR:
            self.log.error('%s', msg_txt)

    def _get_status_message(self, force_log=False):
        """
        Get the status message from the motor if the PV exists.

        :return: tuple with status and message to display, empty string message
        if status is OK.
        """

        stat = SEVERITY_TO_STATUS.get(self._get_pv('alarm_severity'),
                                      status.UNKNOWN)
        if stat == status.UNKNOWN:
            stat = status.ERROR

        if self.errormsgpv:
            msg_txt = self._get_pv('errormsgpv', as_string=True)
        elif stat == status.WARN or stat == status.ERROR:
            msg_txt = self._default_errormsg
        else:
            msg_txt = ''

        if not msg_txt and (stat == status.WARN or stat == status.ERROR):
            msg_txt = self._default_errormsg

        # Avoid repeating the same error message over and over in the log.
        (cached_stat, cached_msg_txt) = self.cached_status
        if force_log or cached_stat != stat or cached_msg_txt != msg_txt:
            self._log_status_error(stat, msg_txt)

            # Cache the new motor status
            self._setROParam('cached_status', (stat, msg_txt))
        return stat, msg_txt

    def doStatus(self, maxage=0):
        moving = self._get_pv('moving')
        startup_failed = False

        # Is the motor currently starting a movement?
        if self._start_time and not moving:
            if time.time() < self._start_time + self.startdelay:
                # We're still in the startup procedure
                return status.BUSY, 'starting'
            elif not self.isAtTarget():
                # Startup waiting timed out, but motor is not at its target.
                # Check for errors and force-write them to the logs.
                startup_failed = True
            self._start_time = None

        # General error check
        stat, message = self._get_status_message(startup_failed)
        if stat in (status.ERROR, status.WARN):
            return stat, message or 'Unknown problem'
        elif startup_failed:
            return status.ERROR, 'starting %s failed' %self

        if self._get_pv('donemoving') == 0 or moving != 0:
            return status.BUSY, message or 'Motor is moving to target...'

        high_limitswitch = self._get_pv('highlimitswitch')
        if high_limitswitch != 0:
            return status.WARN, message or 'At high limit switch.'

        low_limitswitch = self._get_pv('lowlimitswitch')
        if low_limitswitch != 0:
            return status.WARN, message or 'At low limit switch.'

        limit_violation = self._get_pv('softlimit')
        if limit_violation != 0:
            return status.WARN, message or 'Soft limit violation.'

        return status.OK, message

    def doStop(self):
        # The stop field resets itself immediately after it has been written to
        self._put_pv('stop', 1)

        # Block the session until either the stop has been successfull
        # (motor is not moving anymore) or the check loop ran longer than
        # self._stop_delay.
        reset_time = time.time()
        while reset_time + self._stop_delay > time.time():
            done_moving = self._get_pv('donemoving')
            moving = self._get_pv('moving')
            if done_moving and not moving:
                break
            session.delay(self._base_loop_delay)

    def doReadEpics_Abslimits(self):
        absmin = self._get_pv('lowlimit')
        absmax = self._get_pv('highlimit')
        return absmin, absmax

    def doReadSpeedlimits(self):
        basespeed = self._get_pv('basespeed')
        maxspeed = self._get_pv('maxspeed')

        # maxspeed == 0 in the EPICS motor record means that the maximum
        # velocity range checking is disabled. In NICOS, we replace this zero
        # value for maxspeed with infinity, so the NICOS user can clearly
        # understand that there is no maximum speed limit. See also
        # https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_motion
        if maxspeed == 0:
            maxspeed = np.inf

        return basespeed, maxspeed

    def doReadAbslimits(self):
        offset = self.offset
        absmin, absmax = self.epics_abslimits
        return absmin + offset, absmax + offset

    def doReference(self):
        # The reference field resets itself immediately after it has been
        # written to
        self._put_pv('home%s' % self.reference_direction, 1)

        # This function should only return once the reference drive is finished
        # (16th bit of the MSTA field is 1). This function blocks until either
        # this bit has been set or the motor reports movement done for a certain
        # time period
        movement_done_period = 1  # Seconds
        movement_done_start = None
        stat = status.OK

        while True:

            # Performing a reference run, but the status is still idle?
            # If so, force a poll
            if stat == status.OK:
                (stat, _) = self.status(0)

            # Read the 16th bit from the .MSTA field
            status_bits = format(int(self._get_pv('status')), '016b')
            homed = int(status_bits[15])

            # The motor record resets the homing fields to zero once it is done,
            # see https://epics.anl.gov/bcda/synApps/motor/motorRecord.html#Fields_command
            if homed or (not self._get_pv('homeforward') and not self._get_pv('homereverse')):
                # Update the status of the motor so it shows idle
                self.status(0)
                return

            # If the motor reports donemoving for a certain time period, assume that the
            # reference drive is done
            if self._get_pv('donemoving'):
                if movement_done_start:
                    if time.monotonic() > movement_done_start + movement_done_period:
                        # Update the status of the motor so it shows idle
                        self.status(0)
                        return
                else:
                    movement_done_start = time.monotonic()
            else:
                movement_done_start = None

            session.delay(self._base_loop_delay)

    def doReset(self):
        if self.reseterrorpv:
            self._put_pv_readback_checked('reseterrorpv', 1,
                                            timeout=self.epicstimeout)

            # Block the session until either the reset has been successfull
            # (error state has been resolved) or the check loop ran longer than
            # self._reset_delay.
            reset_time = time.time()
            while reset_time + self._reset_delay > time.time():
                # Read out the severity field to see whether the motor is still
                # in error mode
                stat = SEVERITY_TO_STATUS.get(self._get_pv('alarm_severity'),
                                              status.UNKNOWN)
                if stat != status.ERROR:
                    break
                session.delay(self._base_loop_delay)

    def doEnable(self, on):
        self._put_pv('enable', int(on), timeout=None)

    def doWriteDirection(self, value):
        # 0 = positive direction, 1 = negative direction (see motor record docs)
        self._put_pv('direction', value == 'reverse')

    def doReadDirection(self):
        if self._get_pv('direction'):
            return 'reverse'
        return 'forward'

    def doPoll(self, n, maxage):
        self.pollParams('speed', 'speedlimits', 'offset', 'abslimits',
                        'reference_direction')
