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

"""Devices related to the camera focussing."""

from __future__ import absolute_import, division, print_function

from nicos.core.params import Param, dictof, limits
from nicos.devices.generic import Axis


class FocusRing(Axis):

    parameters = {
        'lenses': Param('Defintion of userlimits for each of the lenses.',
                        type=dictof(str, limits), settable=False,
                        mandatory=True, userparam=False),
        'lens': Param('Currently used lens',
                      type=str, userparam=True, settable=True, default=''),
    }

    def doPreInit(self):
        pass

    def doReference(self):
        """Do a reference drive.

        Since the motor has no limit switches the motor has to move to the
        lowest position. It will stop due to the mechanical movement limitation
        and this position will be set to 'absmin'.
        """
        if self._hascoder:
            self.log.error('This is an encoded axis, no need to reference')
            return
        motor = self._attached_motor
        _userlimits = motor.userlimits  # store user limits
        # The use of _setROParam suppresses output to inform users about
        # changing of the user limits
        motor._setROParam('userlimits', motor.abslimits)  # open limits
        try:
            motor.setPosition(motor.absmax)
            motor.maw(motor.absmin)
        finally:
            motor._setROParam('userlimits', _userlimits)  # restore user limits

    def doWriteLens(self, value):
        if value not in self.lenses:
            raise ValueError('Lens is not defined. Possible lenses are: %s' %
                             ', '.join(["'%s'" % x
                                        for x in list(self.lenses.keys())]))
        self.userlimits = self.lenses[value]
