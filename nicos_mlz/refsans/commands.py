#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#  Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special commands only useable at REFSANS"""

from __future__ import absolute_import, division, print_function

from nicos.commands import helparglist, parallel_safe, usercommand
from nicos.commands.device import move


@usercommand
@helparglist('wlmin, wlmax, [D=22.8, chopper2_pos=3, gap=0.1]')
@parallel_safe
def chopper_config(wl_min, wl_max, D=22.8, chopper2_pos=3, gap=.1):
    """Configures the chopper.

    The chopper system will be moved to the settings for speed, and chopper
    disc phases according to the given parameters.

    Examples:

    >>> chopper_config(0, 22) # D=22.8, chopper2_pos=3, gap=0.1
    >>> chopper_config(0, 22, 21.455)  # chopper2_pos=3, gap=0.1
    >>> chopper_config(0, 22, 21.455, 1)  # gap=0.1
    >>> chopper_config(0, 22, 21.455, 2, 0.1)

    """
    target = {
        'wlmin': wl_min,
        'wlmax': wl_max,
        'D': D,
        'chopper2_pos': chopper2_pos,
        'gap': gap
    }
    move('chopper', target)
