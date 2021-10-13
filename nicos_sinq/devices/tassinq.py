#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core.errors import ProgrammingError
from nicos.core.params import Override
from nicos.devices.generic.mono import to_k
from nicos.devices.tas import TAS


class SinqTAS(TAS):
    """
    This just makes the sure that the scanconstant is read from
    the proper device, as requested by the scanmode
    """
    parameter_overrides = {
        'scanconstant': Override(settable=False, volatile=True),
    }

    def doReadScanconstant(self):
        if self.scanmode == 'CKI' or self.scanmode == 'DIFF':
            return to_k(self._attached_mono.read(0),
                        self._attached_mono.unit)
        elif self.scanmode == 'CKF':
            return to_k(self._attached_ana.read(0),
                        self._attached_ana.unit)
        elif self.scanmode == 'CPSI':
            return self._attached_psi.read()
        elif self.scanmode == 'CPHI':
            return self._attached_phi.read(0)
        else:
            raise ProgrammingError()
