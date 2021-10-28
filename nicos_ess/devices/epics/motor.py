#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Michael Wedel <michael.wedel@esss.se>
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from time import time as currenttime

from nicos.core import ADMIN, Override, Param, oneof, pvname, status
from nicos.core.device import requires
from nicos.core.errors import ConfigurationError
from nicos.core.mixins import CanDisable, HasOffset
from nicos.devices.abstract import CanReference, Motor
from nicos.devices.epics import SEVERITY_TO_STATUS, PVMonitor

from nicos_ess.devices.epics.base import EpicsAnalogMoveableEss


class EpicsMotor(CanDisable, CanReference, HasOffset, EpicsAnalogMoveableEss,
                 Motor):
    """
    This device exposes some of the functionality provided by the EPICS motor
    record. The PV names for the fields of the record (readback, speed, etc.)
    are derived by combining the motorpv-parameter with the predefined field
    names.

    The errorbitpv and reseterrorpv can be provided optionally in case the
    controller supports reporting errors and a reset-mechanism that tries to
    recover from certain errors. If present, these are used when calling the
    reset()-method.

    Another optional PV is the errormsgpv, which contains an error message that
    may originate from the motor controller or the IOC. If it is present,
    doStatus uses it for some of the status messages.
    """
    parameters = {
        'motorpv': Param('Name of the motor record PV.', type=pvname,
                         mandatory=True, settable=False, userparam=False),
        'errormsgpv': Param('Optional PV with error message.', type=pvname,
                            mandatory=False, settable=False, userparam=False),
        'errorbitpv': Param('Optional PV with error bit.', type=pvname,
                            mandatory=False, settable=False, userparam=False),
        'reseterrorpv': Param('Optional PV with error reset switch.',
                              type=pvname, mandatory=False, settable=False,
                              userparam=False),
        'reference_direction': Param('Reference run direction.',
                                     type=oneof('forward', 'reverse'),
                                     default='forward', settable=False,
                                     userparam=False, mandatory=False)
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),

        # speed, limits and offset may change from outside, can't rely on cache
        'speed': Override(volatile=True),
        'offset': Override(volatile=True, chatty=False),
        'abslimits': Override(volatile=True),
    }

    _motor_status = (status.OK, '')

    # Fields of the motor record for which an interaction via Channel Access
    # is required.
    def _get_record_fields(self):
        return {
            'readpv': 'RBV',
            'writepv': 'VAL',
            'stop': 'STOP',
            'donemoving': 'DMOV',
            'moving': 'MOVN',
            'miss': 'MISS',
            'homeforward': 'HOMF',
            'homereverse': 'HOMR',
            'speed': 'VELO',
            'offset': 'OFF',
            'highlimit': 'HLM',
            'lowlimit': 'LLM',
            'softlimit': 'LVIO',
            'lowlimitswitch': 'LLS',
            'highlimitswitch': 'HLS',
            'enable': 'CNEN',
            'set': 'SET',
            'foff': 'FOFF',
            'alarm_status': 'STAT',
            'alarm_severity': 'SEVR',
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

        if self.errorbitpv:
            pvs.add('errorbitpv')

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
        motor_record_prefix = getattr(self, 'motorpv')
        motor_field = self._record_fields.get(pvparam)

        if motor_field is not None:
            return '.'.join((motor_record_prefix, motor_field))

        return getattr(self, pvparam)

    def doReadSpeed(self):
        return self._get_pv('speed')

    def doWriteSpeed(self, newValue):
        speed = self._get_valid_speed(newValue)

        if speed != newValue:
            self.log.warning('Selected speed %s is outside the parameter '
                             'limits, using %s instead.', newValue, speed)

        self._put_pv('speed', speed)

    def doReadOffset(self):
        return self._get_pv('offset')

    def doWriteOffset(self, value):
        # In EPICS, the offset is defined in following way:
        # USERval = HARDval + offset

        if self.offset != value:
            diff = value - self.offset

            # Set the offset in motor record
            self._put_pv_blocking('offset', value)

            # Read the absolute limits from the device as they have changed.
            self.abslimits  # pylint: disable=pointless-statement

            # Adjust user limits
            self.userlimits = (
                self.userlimits[0] + diff, self.userlimits[1] + diff)

            self.log.info('The new user limits are: ' + str(self.userlimits))

    def doAdjust(self, oldvalue, newvalue):
        diff = oldvalue - newvalue
        # For EPICS the offset sign convention differs to that of the base
        # implementation.
        self.offset -= diff

    def _get_valid_speed(self, newValue):
        min_speed = self._get_pvctrl('speed', 'lower_ctrl_limit', 0.0)
        max_speed = self._get_pvctrl('speed', 'upper_ctrl_limit', 0.0)

        valid_speed = newValue
        if min_speed != 0.0:
            valid_speed = max(min_speed, valid_speed)

        if max_speed != 0.0:
            valid_speed = min(max_speed, valid_speed)

        return valid_speed

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, target):
        self._put_pv('writepv', target)

    def doReadTarget(self):
        return self._get_pv('writepv')

    def doStatus(self, maxage=0):
        stat, message = self._get_status_message()
        self._motor_status = stat, message
        if stat == status.ERROR:
            return stat, message or 'Unknown problem in record'
        elif stat == status.WARN:
            return stat, message

        done_moving = self._get_pv('donemoving')
        moving = self._get_pv('moving')
        if done_moving == 0 or moving != 0:
            return status.BUSY, message or 'Motor is moving to target...'

        miss = self._get_pv('miss')
        if miss != 0:
            return (
                status.NOTREACHED, message or 'Did not reach target position.')

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

    def _get_status_message(self):
        """
        Get the status message from the motor if the PV exists.

        :return: tuple with status and message to display, empty string message
        if status is OK.
        """
        msg_txt, alarm_severity, alarm_status = self._read_epics_alarm_pvs()
        if msg_txt:
            if alarm_status == 'COMM' and alarm_severity == status.UNKNOWN:
                alarm_severity = status.ERROR
            if self._motor_status != (alarm_severity, msg_txt):
                self._log_epics_msg_info(msg_txt, alarm_severity, alarm_status)
            return alarm_severity, msg_txt
        else:
            return status.OK, ''

    def _read_epics_alarm_pvs(self):
        """
        :return: tuple containing alarm message, severity and status
        """
        if self.errormsgpv:
            return (self._get_pv('errormsgpv', as_string=True),
                    SEVERITY_TO_STATUS.get(self._get_pv('alarm_severity'),
                                           status.UNKNOWN),
                    self._get_pv('alarm_status', as_string=True))
        else:
            return '', status.OK, ''

    def _log_epics_msg_info(self, msg_txt, stat, epics_status):
        if stat == status.OK or stat == status.UNKNOWN:
            return
        msg_to_log = '%s (%s)'
        if stat == status.WARN:
            self.log.warning(msg_to_log, msg_txt, epics_status)
        elif stat == status.ERROR:
            self.log.error(msg_to_log, msg_txt, epics_status)

    def doStop(self):
        self._put_pv('stop', 1, False)

    def _checkLimits(self, limits):
        # Called by doReadUserlimits and doWriteUserlimits
        low, high = self.abslimits
        if low == 0 and high == 0:
            # No limits defined in IOC.
            # Could be a rotation stage for example.
            return

        if limits[0] < low or limits[1] > high:
            raise ConfigurationError('cannot set user limits outside of '
                                     'absolute limits (%s, %s)' % (low, high))

    def doReadAbslimits(self):
        absmin = self._get_pv('lowlimit')
        absmax = self._get_pv('highlimit')
        return absmin, absmax

    def doReference(self):
        self._put_pv_blocking('home%s' % self.reference_direction, 1)

    def doReset(self):
        if self.errorbitpv and self.reseterrorpv:
            error_bit = self._get_pv('errorbitpv')
            if error_bit == 0:
                self.log.warning(
                    'Error bit is not set, can not reset error state.')
            else:
                self._put_pv('reseterrorpv', 1)

    def _enable(self, on):
        what = 1 if on else 0
        self._put_pv('enable', what, False)

    def doSetPosition(self, pos):
        self._put_pv('set', 1)
        self._put_pv('foff', 1)
        self._put_pv('writepv', pos)
        self._put_pv('set', 0)
        self._put_pv('foff', 0)


class HomingProtectedEpicsMotor(EpicsMotor):
    """
    The only thing that this class adds to EpicsMotor is that
    the reference run can only happen with admin rights
    """

    @requires(level=ADMIN)
    def doReference(self):
        EpicsMotor.doReference(self)


class AbsoluteEpicsMotor(EpicsMotor):
    """
    The instances of this class cannot be homed.
    """
    def doReference(self):
        self.log.warning('This motor does not require '
                         'homing - command ignored')


class EpicsMonitorMotor(PVMonitor, EpicsMotor):
    def doStart(self, target):
        self._put_pv('writepv', target)
        if target != self.doRead():
            self._wait_for_start()

    def _on_status_change_cb(self, pvparam, value=None, char_value='', **kws):
        self._check_move_state_changed(pvparam, value)
        PVMonitor._on_status_change_cb(self, pvparam, value, char_value, **kws)

    def _check_move_state_changed(self, pvparam, value):
        # If the fields indicating whether the device is moving change then
        # the cache needs to be updated immediately.
        if pvparam in ['donemoving', 'moving']:
            self._cache.put(self._name, pvparam, value, currenttime())
