#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""TOFTOF neutron guide/collimator switcher device."""

from __future__ import absolute_import, division, print_function

from nicos.core import Override
from nicos.devices.abstract import CanReference
from nicos.devices.generic import Switcher as GenericSwitcher


class Switcher(GenericSwitcher):
    """
    Switcher, specially adapted to TOFTOF needs

    The neutron guide switcher has two different guides and the job is to
    change between them. Since there is no encoder mounted to check the
    position each change has to start with a reference move, followed by
    the move to the target position.
    """

    parameter_overrides = {
        'precision': Override(default=0.1, mandatory=False),
        'fallback': Override(default='Unknown', mandatory=False),
        'blockingmove': Override(default='False', mandatory=False),
    }

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        if isinstance(self._attached_moveable, CanReference):
            self.log.info('referencing %s...', self._attached_moveable)
            self._attached_moveable.reference()
        else:
            self.log.warning('%s cannot be referenced!',
                             self._attached_moveable)
        self._attached_moveable.start(target)
        if self.blockingmove:
            self._attached_moveable.wait()
