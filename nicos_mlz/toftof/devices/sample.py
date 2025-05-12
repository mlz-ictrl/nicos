# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueter@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF specific sample device."""

from nicos.core import Param, oneof

from nicos_mlz.devices.sample import Sample as NicosSample


class Sample(NicosSample):
    """Special TOFTOF specific sample to store the nature of the sample."""

    parameters = {
        'nature': Param('Nature of the sample, needed for NeXus',
                        type=oneof('powder', 'liquid', 'single crystal'),
                        settable=True, default='powder', category='sample'),
    }
