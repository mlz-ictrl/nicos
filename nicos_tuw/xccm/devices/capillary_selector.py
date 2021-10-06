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
#   Arno Frank <arno.frank@tuwien.ac.at>
#
# *****************************************************************************

from nicos.core import Attach, Moveable, Override, anytype, dictof, \
    floatrange, tupleof
from nicos.devices.generic import MultiSwitcher


class CapillarySelector(MultiSwitcher):

    """
    XCCM: Select one of three capillaries

    Three rough positions the user can switch inbetween. Two translation
    stages are used to change the position, leave precision in setup
    a bit higher to allow the user to do some alignment finetuning.
    """

    attached_devices = {
        'moveables': Attach('The 2 (continuous) devices which are'
                            ' controlled', Moveable, multiple=2),
    }

    parameter_overrides = {
        'mapping':   Override(description='Mapping of state names to 3 values '
                              'to move the moveables to',
                              type=dictof(anytype,
                                          tupleof(float, float))),

        'precision': Override(description='List of allowed deviations from '
                                          'target position', mandatory=True,
                                          type=tupleof(floatrange(0),
                                                       floatrange(0))),
    }
