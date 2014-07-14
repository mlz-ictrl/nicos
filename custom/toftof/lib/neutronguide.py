#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Override
from nicos.devices.abstract import CanReference
from nicos.devices.generic import Switcher

class NeutronGuideSwitcher(Switcher):
    """Switcher, specially adopted to TOFTOF needs"""
    parameter_overrides = {
        'precision' : Override(default=0.1, mandatory=False),
        'fallback'  : Override(default='Unknown', mandatory=False),
        'blockingmove'  : Override(default='False', mandatory=False),
    }

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        if isinstance(self._adevs['moveable'], CanReference):
            self.log.info('referencing %s...' % self._adevs['moveable'])
            self._adevs['moveable'].reference()
            self._adevs['moveable'].wait()
        else:
            self.log.warning('%s cannot be referenced!' %
                             self._adevs['moveable'])
        self._adevs['moveable'].start(target)
        if self.blockingmove:
            self._adevs['moveable'].wait()

