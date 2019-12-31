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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

"""Slit devices in AMOR"""

from __future__ import absolute_import, division, print_function

from nicos.core import HasPrecision, Override, status
from nicos.core.utils import multiStatus
from nicos.devices.generic.slit import SlitAxis
from nicos.pycompat import iteritems


class SlitOpening(HasPrecision, SlitAxis):
    """Device to control the slit opening/height.

    Motor dXt changes moves the slit's top slab in turn changing the
    slit opening. Motor dXb changes the position of the whole slit
    moving it up or down (X is the slit number).

    This device reads the current opening using the motor dXt and
    changes the opening using combination of the motors dXt and dXb
    such that the center remains aligned.
    """

    parameter_overrides = {
        'unit': Override(mandatory=False, default='mm'),
        'fmtstr': Override(userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False),
        'precision': Override(userparam=False, default=0.01),
        'target': Override(volatile=True)
    }

    status_to_msg = {
        status.ERROR: 'Error in %s',
        status.BUSY: 'Moving: %s ...',
        status.WARN: 'Warning in %s',
        status.NOTREACHED: '%s did not reach target!',
        status.UNKNOWN: 'Unknown status in %s!',
        status.OK: 'Ready.'
    }

    def doReadTarget(self):
        # Do not allow None as target
        target = self._getFromCache('target', self.doRead)
        return target if target is not None else self.doRead(0)

    def _convertRead(self, positions):
        return positions[3]

    def _convertStart(self, target, current):
        current_opening = current[3]
        current_bottom = current[2]
        new_bottom = current_bottom + 0.5 * (current_opening - target)
        return current[0], current[1], new_bottom, target

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        st_devs = multiStatus(self._adevs, maxage)
        devs = [dname for dname, d in iteritems(self._adevs)
                if d.status()[0] == st_devs[0]]

        if st_devs[0] in self.status_to_msg:
            msg = self.status_to_msg[st_devs[0]]
            if '%' in msg:
                msg = msg % ', '.join(devs)
            return st_devs[0], msg

        return st_devs
