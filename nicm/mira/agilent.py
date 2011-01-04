#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Agilent wave generator classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm.utils import oneof
from nicm.device import Param
from nicm.taco.analog import Output


class HFDevice(Output):

    parameters = {
        'shape': Param('Wave shape', type=oneof(str, 'sinusoid', 'square'),
                       settable=True, category='general'),
        'offset': Param('Offset of zero point', type=float, settable=True,
                        category='offsets'),
    }

    def doReadShape(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'shape')

    def doReadOffset(self):
        return float(self._taco_guard(self._dev.deviceQueryResource, 'offset'))

    def doWriteShape(self, val):
        self._taco_update_resource('shape', val)

    def doWriteOffset(self, val):
        self._taco_update_resource('offset', str(val))
