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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core import Param, pvname, status
from nicos_sinq.amor.devices.epics_extensions import EpicsDetector


class EpicsScalerRecord(EpicsDetector):
    """
    Class that implements the neutron counter box present in AMOR
    using the EpicsDetector class.

    This counter box can set one time preset and one count preset,
    To use the time preset, the count preset should be set to 0 and
    vice-a-versa.

    In addition to the standard detector start/pause functions few
    more pvs are provided that provide details on the status and the
    driver error messages from the counter box

    Following codes are used for status:

    * 0 - Ok, but not counting
    * 1 - Currently counting
    * 2 - No beam present
    * 3 - Counting paused
    """

    parameters = {
        'statuspv': Param('Optional PV describing status of the counter',
                          type=pvname),
        'errormsgpv': Param('Optional PV providing the error message',
                            type=pvname),
    }

    def _get_pv_parameters(self):
        pvs = EpicsDetector._get_pv_parameters(self)

        if self.statuspv:
            pvs.add('statuspv')

        if self.errormsgpv:
            pvs.add('errormsgpv')

        return pvs

    def doSetPreset(self, **preset):
        # The counter box can set one time and count preset. If the time
        # preset is set, auto set the count preset to 0 and vice-a-versa.
        # Both presets cannot be set at a time.

        # This represents the various possible count and time presets
        countpreset = set(preset).intersection(['det1', 'ctr1', 'n'])
        timepreset = set(preset).intersection(['timer1', 'time', 't'])

        # Check if user set both time and count preset
        if countpreset and timepreset:
            self.log.debug('Both count and time preset cannot be set at '
                           'the same time.')
            self.log.debug('Using just the count preset.')
            for name in timepreset:
                preset.pop(name)
            timepreset = set()

        if timepreset:
            preset['n'] = 0
            self.log.debug('Setting time preset of %f',
                           preset[timepreset.pop()])
            self.log.debug('Also updating the count preset to 0')

        if countpreset:
            preset['t'] = 0
            self.log.info('Setting count preset of %d',
                          preset[countpreset.pop()])
            self.log.info('Also updating the time preset to 0')

        # Let the parent handle the rest
        EpicsDetector.doSetPreset(self, **preset)

    def doStatus(self, maxage=0):
        if self.errormsgpv:
            message_text = self._get_pv('errormsgpv').strip()
            if message_text and message_text != 'OK':
                return status.ERROR, message_text

        if self.statuspv:
            status_code = int(self._get_pv('statuspv'))

            if status_code == 0:
                return status.OK, 'Idle'
            elif status_code == 1:
                return status.BUSY, 'Counting'
            elif status_code == 2:
                return status.ERROR, 'No Beam present'
            elif status_code == 3:
                return status.OK, 'Paused'

        return EpicsDetector.doStatus(self, maxage)

    def doInfo(self):
        ret = []

        # Check for the mode and preset
        mode = ''
        value = 0
        unit = ''
        for d in self._masters:
            for k in self._presetkeys:
                if self._presetkeys[k] and self._presetkeys[k].name == d.name:
                    preselection = d.preselection
                    if preselection != 0:
                        value = preselection
                        unit = d.unit
                        mode = 'timer' if k.startswith('t') else 'monitor'
                        break
        ret.append(('mode', mode, mode, '', 'presets'))
        ret.append(('preset', value, '%s' % value, unit, 'presets'))

        # Add rest of the channels to the info as well
        for channel in self._attached_timers + self._attached_counters:
            value = channel.read(0)
            ret.append((channel.name, value, '%s' % value,
                        channel.unit, 'presets'))

        return ret
