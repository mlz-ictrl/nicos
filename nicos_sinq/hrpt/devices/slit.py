#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""HRPT slit device."""

from nicos.core import Param

from nicos_mlz.refsans.devices.slits import CenterGapAxis, Gap as DefaultGap, \
    GapAxis


class WidthGapAxis(GapAxis):

    def _convertRead(self, positions):
        return (positions[1] - positions[0]) / \
               self._attached_gap.conversion_factor

    def _convertStart(self, target, current):
        center = (current[0] + current[1]) / 2.
        return (center - target / 2 * self._attached_gap.conversion_factor,
                center + target / 2 * self._attached_gap.conversion_factor)


class Gap(DefaultGap):

    parameters = {
        'conversion_factor': Param('Conversion between motor readout and width',
                                   type=float, default=22.66, userparam=False)
    }

    def doInit(self, mode):
        self._axes = [self._attached_left, self._attached_right]
        self._axnames = ['left', 'right']

        for name in self._axnames:
            self.__dict__[name] = self._adevs[name]

        # TODO: needs to use HasAutoDevices?
        for name, cls in [('center', CenterGapAxis), ('width', WidthGapAxis), ]:
            self.__dict__[name] = cls('%s.%s' % (self.name, name), gap=self,
                                      unit=self.unit, visibility=())
