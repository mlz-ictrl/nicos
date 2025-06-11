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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Class for PUMA stt axis."""

from nicos.core import Attach, Moveable, Param
from nicos.devices.generic.axis import Axis


class CombAxis(Axis):
    """Class for PUMA stt axis.

    When sth axis must stay at the same angle relative to the incoming beam.
    For example, when the magnet is used
    """

    attached_devices = {
        'fix_ax': Attach('axis that moves back', Moveable),
    }

    parameters = {
        'iscomb': Param('If it is combined or normal axis',
                        type=bool, default=False, mandatory=True,
                        settable=True),
    }

    _fixpos = None

    def doInit(self, mode):
        Axis.doInit(self, mode)
        self._update_fixpos(self.iscomb)

    def doWriteIscomb(self, val):
        self._update_fixpos(val)

    def _update_fixpos(self, val):
        self._fixpos = self.read(0) + self._attached_fix_ax.read(0) if val \
            else None

    def doIsAllowed(self, target):
        mainax = Axis.doIsAllowed(self, target)
        if not self.iscomb:
            return mainax
        relpos = self._fixpos - target
        fixax = self._attached_fix_ax.isAllowed(relpos)
        if mainax[0] and fixax[0]:
            return True, 'Ok'
        return False, '%s: %s, %s: %s' % \
            (self, mainax[1], self._attached_fix_ax, fixax[1])

    def _postMoveAction(self):
        if self.iscomb:
            relpos = self._fixpos - self.read(0)
            self._attached_fix_ax.maw(relpos)
