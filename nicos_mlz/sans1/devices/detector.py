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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Special detector devices for the SANS1"""

from nicos.core.mixins import DeviceMixinBase
from nicos.core.params import Param, floatrange, tupleof
from nicos.devices.generic import Detector as GenericDetector, \
    GatedDetector as GenericGatedDetector


class DetectorMixin(DeviceMixinBase):
    """Provide the size parameter."""
    parameters = {
        'size': Param('size of the active detector area',
                      type=tupleof(floatrange(0), floatrange(0)),
                      settable=False, mandatory=False, unit='mm',
                      default=(1000., 1000.)),
    }


class Detector(DetectorMixin, GenericDetector):
    """Standard detector including its size."""


class GatedDetector(DetectorMixin, GenericGatedDetector):
    """Standard gated detector including its size."""
