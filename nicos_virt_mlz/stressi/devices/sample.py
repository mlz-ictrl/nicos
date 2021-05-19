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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""VStressi sample device."""

from nicos.core import Param, intrange
from nicos.devices.sample import Sample as BaseSample


class Sample(BaseSample):

    parameters = {
        'sampletype': Param('Sample type: '
                            '1 - Abs experiment FoPra '
                            '2 - Strain experiment FoPra E-Mod 211 '
                            '3 - Strain experiment FoPra E-Mod 200 '
                            '4 - fully flexible sample',
                            type=intrange(1, 4), userparam=True,
                            settable=True),
    }
