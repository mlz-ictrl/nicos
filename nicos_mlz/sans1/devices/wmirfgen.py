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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for the WMI microwave generator."""


from nicos.core import Param, oneof
from nicos.devices.tango import AnalogOutput


class Frequency(AnalogOutput):
    """Device for RF generator frequency and frequency modulation settings."""
    parameters = {
        'deviation': Param('FM signal deviation', type=float, settable=True),
        'modulationsource': Param('Modulation source', type=oneof('internal_1',
                                                                  'internal_2',
                                                                  'external_1',
                                                                  'noise'),
                                  settable=True),
        'enablemodulation': Param('Enable frequency modulation', type=bool,
                                  settable=True),
    }

    def doReadDeviation(self):
        return self._dev.moddeviation

    def doWriteDeviation(self, value):
        self._dev.moddeviation = value

    def doReadModulationsource(self):
        return self._dev.modsource

    def doWriteModulationsource(self, value):
        self._dev.modsource = value

    def doReadEnablemodulation(self):
        return self._dev.modulation

    def doWriteEnablemodulation(self, value):
        self._dev.modulation = value
