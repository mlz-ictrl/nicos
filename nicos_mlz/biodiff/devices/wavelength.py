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
#
# *****************************************************************************

"""BIODIFF wavelength selection device."""

from nicos.core.device import Moveable
from nicos.core.params import Attach
from nicos.devices.generic.sequence import LockedDevice, SeqDev


class WaveLength(LockedDevice):
    """Wavelength selection device.

    The selection of the wavelength at the instrument is done with the help of
    2 devices, a monochromator crystal followed by a selector device to remove
    the higher order reflections.

    The selector is mounted on the 2theta arm of the monochromator and it
    isn't allowed to be moved around the monochromator table until a certain
    (or minimum) rotation speed is reached.

    After adjusting the monochromator crystal to the desired wavelength the
    selector itself has to be adjusted to this wavelength as well.

    In the configuration the `lock` device should be the selector speed device
    and the `device` the crystal monochromator device.
    """

    attached_devices = {
        'selector': Attach('Velocity selector device', Moveable),
    }

    def _generateSequence(self, target):
        seq = LockedDevice._generateSequence(self, target)
        seq.append(SeqDev(self._attached_selector, target))
        return seq
