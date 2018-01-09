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
#   Christian Franz <christian.franz@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Readable, Override, Attach, status

class wavelength(Readable):

    attached_devices = {
        'selspeed': Attach('Selector rotation speed in rpm', Readable),
        'tilt': Attach('Selector cradle encoder angle in deg', Readable),
    }


    parameter_overrides = {
        'unit':  Override(mandatory=False, default='A'),
    }

    def doRead(self, maxage=0):

        speed= self._attached_selector_speed.read(maxage)
        tilt = self._attached_selcradle.read(maxage)

        alpha = 48.27    # screw angle in deg
        L = 250.0          # selector length in mm
        R = 160.0          # selector radius in mm

        lambda_ = 6.59e5 * (alpha * L/R * tilt) / (speed * L)

        return lambda_


    def doStatus(self, maxage=0):
        return status.OK, ''
