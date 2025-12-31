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

"""Sample changer devices."""

from nicos import session
from nicos.core.mixins import Override
from nicos.devices.generic import MultiSwitcher


class SampleChanger(MultiSwitcher):
    """Sample changer device.

    It selects the sample after reaching the target.
    """

    parameter_overrides = {
        'blockingmove': Override(default=True, settable=False),
    }

    def doStart(self, target):
        if self.doRead(0) != target:
            return self._startRaw(self._mapTargetValue(target))

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        samplenr = int(self._mapReadValue(target)[1:])
        self.log.debug('move to: %s %s', target, samplenr)
        MultiSwitcher._startRaw(self, target)
        session.experiment.sample.select(samplenr)
