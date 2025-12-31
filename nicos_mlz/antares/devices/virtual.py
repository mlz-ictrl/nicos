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
#   Simon Sebold <simon.sebold@frm2.tum.de>
#
# *****************************************************************************

from pathlib import Path

from nicos.core import Attach, Moveable, Param, absolute_path
from nicos.devices.generic import Pulse, VirtualTimer


class TriggerTimer(VirtualTimer):
    """Virtual timer starting an exernal device via a pulse."""

    attached_devices = {
        'trigger': Attach('Pulser device', Pulse),
    }

    def doStart(self):
        self._attached_trigger.move(self._attached_trigger.onvalue)
        VirtualTimer.doStart(self)


class TriggerTimerStartStop(VirtualTimer):
    """Virtual timer starting and stopping an external device via pulses."""

    attached_devices = {
        'trigger_start': Attach('Device triggered at start of timer',
                                Pulse),
        'trigger_stop': Attach('Device triggered at end of timer',
                               Pulse),
    }

    def doStart(self):
        self._attached_trigger_start.move(self._attached_trigger_start.onvalue)
        VirtualTimer.doStart(self)

    def doFinish(self):
        VirtualTimer.doFinish(self)
        self._attached_trigger_stop.move(self._attached_trigger_stop.onvalue)


class TriggerTimerStatus(VirtualTimer):
    """Virtual Timer moving an external device to a run and stop value."""

    attached_devices = {
        'moveable': Attach('Device triggered', Moveable),
    }

    parameters = {
        'runvalue': Param('Value of moveable while timer is running',
                          type=str, mandatory=True),
        'stopvalue': Param('Value of moveable while timer is stopped',
                           type=str, mandatory=True),
    }

    def doStart(self):
        self._attached_moveable.move(self.runvalue)
        VirtualTimer.doStart(self)

    def doFinish(self):
        VirtualTimer.doFinish(self)
        self._attached_moveable.move(self.stopvalue)


class TriggerTimerStatusFile(VirtualTimer):
    """Virtual timer creating a file when starting and remove after finishing."""

    parameters = {
        'filepath': Param('Value of moveable while timer is running',
                          type=absolute_path, mandatory=True),
    }

    def doStart(self):
        Path(self.filepath).touch()
        VirtualTimer.doStart(self)

    def doFinish(self):
        VirtualTimer.doFinish(self)
        # Path(self.filepath).unlink(True)
