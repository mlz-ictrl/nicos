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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Class for PUMA phi axis when psi axis must stay at the same angle relative
to the incoming beam.
For example, when the magnet is used
"""

from nicos.core import Moveable, Param, Attach, status


class CombAxis(Moveable):

    attached_devices = {
        'main_ax': Attach('moving axis', Moveable),
        'fix_ax': Attach('axis that moves back', Moveable),
    }

    parameters = {
        'iscomb': Param('If it is combined or normal axis', default=False,
                        mandatory=True, settable=True, type=bool),
    }

    def doInit(self, mode):
        if self.iscomb:
            self._fixpos = self._attached_main_ax.read(0) + \
                self._attached_fix_ax.read(0)
        else:
            self._fixpos = None

    def doWriteIscomb(self, val):
        if val:
            self._fixpos = self._attached_main_ax.read(0) + \
                self._attached_fix_ax.read(0)

    def doIsAllowed(self, pos):
        mainax = self._attached_main_ax.isAllowed(pos)
        if not self.iscomb:
            return mainax
        relpos = self._fixpos - pos
        fixax = self._attached_fix_ax.isAllowed(relpos)
        if mainax[0] and fixax[0]:
            return (True, 'Ok')
        else:
            return (False, '%s: %s, %s: %s' % (self._attached_main_ax,
                                               mainax[1],
                                               self._attached_fix_ax,
                                               fixax[1]))

    def doRead(self, maxage=0):
        return self._attached_main_ax.read(maxage)

    def doStart(self, pos):
        self._attached_main_ax.start(pos)

    def doOldWait(self):
        self._attached_main_ax.wait()
        if self.iscomb:
            relpos = self._fixpos - self._attached_main_ax.read(0)
            self._attached_fix_ax.start(relpos)  # ??? start here?????
            self._attached_fix_ax.wait()

    def doStatus(self, maxage=0):
        mainax = self._attached_main_ax.status(maxage)
        if not self.iscomb:
            return mainax
        if mainax[0] == status.BUSY or mainax[0] == status.ERROR:
            return mainax
        return self._attached_fix_ax.status(maxage)
