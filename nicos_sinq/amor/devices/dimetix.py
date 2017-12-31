#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core import status
from nicos.devices.epics import EpicsReadable
from nicos_ess.devices.epics.extensions import HasSwitchPv


class EpicsDimetix(HasSwitchPv, EpicsReadable):
    """ AMOR's laser distance measurement device called dimetix.
    """
    def doStatus(self, maxage=0):
        if not self.isSwitchedOn:
            return status.WARN, 'Laser OFF'

        return EpicsReadable.doStatus(self, maxage)
