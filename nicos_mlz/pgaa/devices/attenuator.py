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

"""The PGAA attenuator."""

from nicos.core import Override, multiWait
from nicos.core.device import Moveable
from nicos.core.errors import InvalidValueError
from nicos.core.params import Attach
from nicos.devices.generic.switcher import MultiSwitcher


class Attenuator(MultiSwitcher):
    """Attenuator with 3 elements."""

    attached_devices = {
        'moveables': Attach('The 3 devices which are controlled', Moveable,
                            multiple=3),
    }

    parameter_overrides = {
        'unit': Override(default='%', settable=False, mandatory=False, ),
        'fmtstr': Override(default='%.f', mandatory=False, ),
    }

    def _startRaw(self, target):
        """Target is the raw value, i.e. a list of positions."""
        moveables = self._attached_moveables
        if not isinstance(target, (tuple, list)) or \
                len(target) < len(moveables):
            raise InvalidValueError(self, 'doStart needs a tuple of %d '
                                    'positions for this device!' %
                                    len(moveables))
        # only check and move the moveables, which are first in self.devices
        for d, t in zip(moveables, target):
            if not d.isAllowed(t):
                raise InvalidValueError(self, f'target value {t!r} not '
                                        f'accepted by device {t.name}')
        # Move first in all needed blades into the beam to reduce the
        # activation of sample and/or save the detector and them move out the
        # not needed ones
        for d, t in zip(moveables, target):
            self.log.debug('moving %r to %r', d, t)
            if t == 'in':
                d.start(t)
        for d, t in zip(moveables, target):
            self.log.debug('moving %r to %r', d, t)
            if t == 'out':
                d.start(t)
        if self.blockingmove:
            multiWait(moveables)
