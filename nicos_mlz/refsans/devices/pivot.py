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
#   Matthias Pomm <matthias.pomm@hzg.de> 2018-08-08 08:33:38
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.core import Override, Param, floatrange
from nicos.core.utils import ADMIN
from nicos.devices.generic import ManualSwitch


class PivotPoint(ManualSwitch):

    parameters = {
        'grid': Param('Distance between the possible points',
                      type=floatrange(0), settable=False, userparam=False,
                      default=125., unit='mm'),
        'height': Param('Height above ground level',
                        type=floatrange(0), settable=False, default=373,
                        unit='mm'),
    }

    parameter_overrides = {
        'requires': Override(default={'level': ADMIN}, settable=False),
    }

    def doStart(self, target):
        ManualSwitch.doStart(self, target)
