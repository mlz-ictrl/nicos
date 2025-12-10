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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""FirePOD specific NICOS GUI input widgets."""

from nicos.clients.gui.cmdlets import Center, Configure, ContScan, Count, \
    CScan, Move, NewSample, Scan, Sleep, TimeScan, WaitFor, deregister, \
    register


class FirePODMove(Move):
    """Cmdlet for move/maw commands with restricted list of devices.

    The names of the devices which should be displayed can be given in an
    option of the command or script builder panel.

    Options:

    * ``movelist`` (default ``['omgs', 'tths', 'xs', 'y']``) -- list of
      device names that should be displayed as possible devices.
    """
    def on_entryAdded(self, entry):
        def on_device_change(text):
            entry.target.dev = text
            self.changed()
        devlist = self.options.get('movelist', ['omgs', 'tths', 'xs', 'ys'])
        entry.device.addItems(self._getDeviceList(f'dn in {devlist!r}'))
        on_device_change(entry.device.currentText())
        entry.device.currentTextChanged.connect(on_device_change)
        entry.target.setClient(self.client)
        entry.target.valueModified.connect(self.changed)


class FirePODScan(Scan):
    """Cmdlet for scan command with restricted list of devices.

    The names of the devices which should be displayed can be given in an
    option of the commdnd or script builder panel.

    * ``scanlist`` (default ``['omgs']``) -- list of device names that should
      be displayed as possible devices.
    """
    def __init__(self, parent, client, options):
        Scan.__init__(self, parent, client, options)
        devlist = self.options.get('scanlist', ['omgs',])
        self.device.clear()
        self.device.addItems(self._getDeviceList(f'dn in {devlist!r}'))


for cmdlet in [Move, WaitFor, Count, Scan, CScan, TimeScan, ContScan, Sleep,
               Configure, NewSample, Center]:
    deregister(cmdlet)

for cmdlet in [FirePODMove, FirePODScan]:
    register(cmdlet)
