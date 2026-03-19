# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2026-present by the NICOS contributors (see AUTHORS)
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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

from nicos.core import MASTER, Param, status

from nicos_sinq.devices.epics.shutter import Shutter as BaseShutter


class Shutter(BaseShutter):

    parameters = {
        'overcount_set':
            Param('Overcount protection flag',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                ),
    }

    def doStatus(self, maxage=0):
        status_code, status_msg = BaseShutter.doStatus(self, maxage)
        if 'detector overcount' in status_msg:
            self._setROParam('overcount_set', True)

        if self.overcount_set:
            return status.ERROR, status_msg + ' - overcount protection triggered, reset device to acknowledge'

        return status_code, status_msg

    def doInit(self, mode):
        BaseShutter.doInit(self, mode)
        if mode == MASTER:
            self.overcount_set = False

    def doReset(self):
        BaseShutter.doReset(self)
        self.overcount_set = False
