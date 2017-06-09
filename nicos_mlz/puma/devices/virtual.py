#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
"""PUMA specific virtual devices."""

from nicos.core import Param, none_or
from nicos.devices.abstract import CanReference
from nicos.devices.generic import VirtualMotor


class VirtualReferenceMotor(CanReference, VirtualMotor):
    """Virtual motor device with reference capability."""

    parameters = {
        'refpos': Param('Reference position if given',
                        type=none_or(float), settable=False, default=None,
                        unit='main'),
    }

    def doReference(self, *args):
        if self.refpos is not None:
            return self.setPosition(self.refpos)
        return self.refpos

    def isAtReference(self):
        if self.refpos is None:
            return False
        return abs(self.refpos - self.read()) <= self.precision
