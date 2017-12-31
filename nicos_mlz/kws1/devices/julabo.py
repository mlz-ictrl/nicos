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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Special device for Julabo temperature controllers."""

from nicos.devices.tango import TemperatureController as BaseController


class TemperatureController(BaseController):
    """Because the Julabo has no setting for the temperature ramp, the Tango
    ramp is always zero and doTime() does not work well.

    Use an average value of 3.5 K/min to get a better time estimate.
    """

    def doTime(self, old, new):
        if old is None or new is None or old == new:
            return 0.
        ramp = 3.5  # see docstring
        return abs(new - old) * (60 / ramp) + self.window
