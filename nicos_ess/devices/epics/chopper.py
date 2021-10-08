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
#   Michael Hart <michael.hart@stfc.ac.uk>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************
from nicos.core import Attach, Override, Param, Readable, Waitable, status
from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics import SEVERITY_TO_STATUS, STAT_TO_STATUS
from nicos.devices.epics.pva import EpicsDevice


class ChopperAlarms(EpicsDevice, Readable):
    """
    This device handles chopper alarms.
    """
    parameters = {
        'pv_root': Param('PV root for device', type=str, mandatory=True,
                         userparam=False),
    }
    parameter_overrides = {
        'unit': Override(mandatory=False, settable=False, volatile=False),
    }

    _alarm_state = {}
    _chopper_alarm_names = {'Comm_Alrm', 'HW_Alrm', 'SW_Alrm', 'nTmp_Alrm',
                            'ILck_Alrm', 'Pos_Alrm', 'Ref_Alrm', 'V_Alrm'}
    _record_fields = {}
    _cache_relations = {}

    def doPreinit(self, mode):
        self._alarm_state = {
            name: (status.OK, '')
            for name in self._chopper_alarm_names}

        for pv in self._chopper_alarm_names:
            for pv_field in ['', '.STAT', '.SEVR']:
                self._record_fields[
                    pv + pv_field] = self.pv_root + pv + pv_field
        EpicsDevice.doPreinit(self, mode)

    def _get_pv_parameters(self):
        return set(self._record_fields)

    def _get_status_parameters(self):
        return self._chopper_alarm_names

    def _get_pv_name(self, pvparam):
        return self._record_fields[pvparam]

    def doRead(self, maxage=0):
        return ''

    def doStatus(self, maxage=0):
        """
        Goes through all alarms in the chopper and returns the alarm encountered
        with the highest severity. All alarms are printed in the session log.
        """
        message = ''
        highest_severity = status.OK
        for name in self._chopper_alarm_names:
            pv_value = self._get_pv(name, as_string=True)
            stat = self._get_alarm_status(name)
            severity = self._get_alarm_sevr(name)
            if pv_value:
                if self._alarm_state[name] != (severity, stat):
                    self._write_alarm_to_log(pv_value, severity, stat)
                if severity > highest_severity:
                    highest_severity = severity
                    message = pv_value
            self._alarm_state[name] = severity, stat
        return highest_severity, message

    def _get_alarm_status(self, name):
        status_raw = self._get_pv(name + '.STAT')
        return STAT_TO_STATUS.get(status_raw, status.UNKNOWN)

    def _get_alarm_sevr(self, name):
        severity_raw = self._get_pv(name + '.SEVR')
        return SEVERITY_TO_STATUS.get(severity_raw, status.UNKNOWN)

    def _write_alarm_to_log(self, pv_value, severity, stat):
        msg_format = '%s (%s)'
        if severity in [status.ERROR, status.UNKNOWN]:
            self.log.error(msg_format, pv_value, stat)
        elif severity == status.WARN:
            self.log.warning(msg_format, pv_value, stat)


class EssChopperController(MappedMoveable):
    """Handles the status and hardware control for an ESS chopper system"""

    attached_devices = {
        'state': Attach('Current state of the chopper', Readable),
        'command': Attach('Command PV of the chopper', MappedMoveable),
        'alarms': Attach('Alarms of the chopper', ChopperAlarms, optional=True)
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'unit': Override(mandatory=False),
        'mapping': Override(mandatory=False, settable=False, userparam=False,
                            volatile=True)
    }

    hardware_access = False
    valuetype = str

    def doRead(self, maxage=0):
        return self._attached_state.read()

    def doStart(self, target):
        self._attached_command.move(target)

    def doStop(self):
        # Ignore - stopping the chopper is done via the move command.
        pass

    def doReset(self):
        # Ignore - resetting the chopper is done via the move command.
        pass

    def doStatus(self, maxage=0):
        if self._attached_alarms:
            stat, msg = self._attached_alarms.doStatus(maxage)
            if stat != status.OK:
                return stat, msg
        stat, msg = Waitable.doStatus(self, maxage)
        if stat != status.OK:
            return stat, msg
        return status.OK, ''

    def doReadMapping(self):
        return self._attached_command.mapping
