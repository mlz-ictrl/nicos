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
#   Mark.Koennecke@psi.ch
#   Michele.Brambilla@psi.ch
#
# *****************************************************************************

"""
SINQ  monochromator

SINQ uses a different way to calculate monochromator focusing
"""

from __future__ import absolute_import

from nicos.devices.generic.mono import from_k, to_k
from nicos.devices.tas.mono import Monochromator


class SinqMonochromator(Monochromator):
    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        focusv = self._attached_focusv
        if focusv:
            focusv.move(
                self._calfocus(from_k(to_k(self.target, self.unit), 'A'),
                               vfocuspars))

    def _calfocus(self, lam, focuspars):
        return focuspars[0] + focuspars[1] / (self.target / (2.0 *
                                                             self.dvalue))
