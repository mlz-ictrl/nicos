#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""IPC class to work around reset bug of triple cards from göttingen"""


from nicos.core import usermethod
from nicos.devices.vendor.ipc import Motor as _Motor

# create a workaround class
class Motor(_Motor):
    def doReset(self):
        if self._hwtype == 'single':
            _Motor.reset(self)
        else:
            self.log.warning('Resetting triple cards disabled. If you REALLY '
                             'want to reset, use %s.reallyReset() method' %
                             self.name)

    @usermethod
    def reallyReset(self):
        _Motor.reset(self)
