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
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

from nicos.core import Attach, Waitable,  Param, Override, oneof
from nicos.core.device import Moveable
from nicos.core.utils import multiStatus

class AmorPolarizer(Waitable):
    """
    Handping and reporting on spin state
    """
    parameters = {
        'polconfiglabel': Param('encoding of the polarization set-up',
                                type=float, userparam=True, settable=True,
                                volatile=True),
        'polconfig': Param('managing the polarization', type=oneof(1,2,3),
                           userparam=True, settable=True, volatile=True),
    }

    attached_devices = {
        'pz1': Attach('polarizer lift 1 height', Moveable),
        'pz2': Attach('polarizer lift 2 height', Moveable),
        'spinflipper_amp': Attach('current in the spin flipper', Moveable),
        'polarizer_lift_1_fom': Attach('default value for pz1 in fom mode', Moveable),
        'polarizer_lift_2_fom': Attach('default value for pz2 in fom mode', Moveable),
        'polarizer_lift_1_pol': Attach('default value for pz1 in pol mode', Moveable),
        'polarizer_lift_2_pol': Attach('default value for pz2 in pol mode', Moveable),
        'spin_flipper_current_p': Attach('default value for spinflipper_amp in p mode', Moveable),
    }

    # A "Waitable" by default needs a unit. Here this does not make sense.
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    _wait_for = []

    def _startDevices(self, target):
        for name, value in target.items():
            dev = self._adevs[name]
            dev.start(value)
            self._wait_for.append(dev)

    def _getWaiters(self):
        return self._wait_for

    def doStatus(self, maxage=0):
        return multiStatus(self._adevs)

    def doRead(self, maxage=0):
        pass

    def doReadPolconfiglabel(self):
        spinflipper_amp = self._attached_spinflipper_amp.read(0)
        pz1 = self._attached_pz1.read(0)
        pz2 = self._attached_pz2.read(0)
        if abs(pz1-90)<2 and abs(pz2-90)<2:
            return 1
        elif abs(pz1-14)<2 and abs(pz2-14)<2:
            if abs(spinflipper_amp-1.7) < 0.1:
                return 2
            elif abs(spinflipper_amp) < 0.1:
                return 3
            else:
                return 0
        return 0

    def doReadPolconfig(self):
        spinflipper_amp = self._attached_spinflipper_amp.read(0)
        pz1 = self._attached_pz1.read(0)
        pz2 = self._attached_pz2.read(0)
        if abs(pz1-90)<2 and abs(pz2-90)<2:
            return 1
        elif abs(pz1-14)<2 and abs(pz2-14)<2:
            if abs(spinflipper_amp-1.7) < 0.1:
                return 2
            elif abs(spinflipper_amp) < 0.1:
                return 3
            else:
                return 0
        return 0

    def doWritePolconfig(self, target):
        pz1_off = self._attached_polarizer_lift_1_fom.read(0)
        pz2_off = self._attached_polarizer_lift_2_fom.read(0)
        pz1_on = self._attached_polarizer_lift_1_pol.read(0)
        pz2_on = self._attached_polarizer_lift_2_pol.read(0)
        sfa_on = self._attached_spin_flipper_current_p.read(0)
        target = int(target)
        positions = {}
        if target == 1:
            if self.polconfiglabel in [0, 2, 3]:
                positions['pz1'] = pz1_off
                positions['pz2'] = pz2_off
            positions['spinflipper_amp'] = 0.
            #self.polsymbol = 'o'
        elif target == 2:
            if self.polconfiglabel in [0, 1]:
                positions['pz1'] = pz1_on
                positions['pz2'] = pz2_on
            positions['spinflipper_amp'] = sfa_on
            #self.polsymbol = 'p'
        elif target == 3:
            if self.polconfiglabel in [0, 1]:
                positions['pz1'] = pz1_on
                positions['pz2'] = pz2_on
            positions['spinflipper_amp'] = 0
            #self.polsymbol = 'm'
        self._startDevices(positions)
