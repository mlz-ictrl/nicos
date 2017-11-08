#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""REFSANS neutron guide system class."""

from nicos.core import Moveable, Override, Param, floatrange, none_or, oneof, \
    status  # Attach,

# from nicos_mlz.refsans.devices.nok_support import DoubleMotorNOK

from nicos.pycompat import number_types, string_types


class Optic(Moveable):
    """REFSANS neutron guide system."""

    parameters = {
        'lmode': Param('Lateral mode of the beam',
                       type=oneof('gisans', 'reflectometry'),
                       default='reflectometry', settable=True, userparam=True),
        'collimation': Param('Collimation',
                             type=none_or(oneof('slit', 'point', 'pinhole')),
                             settable=True, userparam=True, default=None),
        'polarisation': Param('Polarisation',
                              type=oneof('up', 'down', 'standby', 'off'),
                              settable=True, userparam=True, default='off'),
    }

    parameter_overrides = {
        'unit': Override(default='mrad', mandatory=False, volatile=True),
    }

    attached_devices = {
        # 'nok2': Attach('NOK 2', DoubleMotorNOK),
    }

    def doInit(self, mode):
        pass

    def doRead(self, maxage=0):
        return self.target

    def doIsAllowed(self, target):
        if isinstance(target, string_types):
            try:
                oneof('horizontal', '12mrad', '48mrad')(target)
                return True, ''
            except ValueError as e:
                return False, e.message
        elif isinstance(target, number_types):
            try:
                floatrange(0, 48)(target)
                return True, ''
            except ValueError as e:
                return False, e.message
        return False, 'Wrong value type'

    def doStart(self, target):
        # Calculate positions and move devices
        # self._attached_nok2.move((0, 0))
        self._pollParam('unit')

    def doWriteLmode(self, value):
        # Calculate the positions for the ...
        self.log.info('Change to: %s', value)
        self._attached_nok2.move((0, 0))

    # def doReadLmode(self):
    #     # Only needed if it could be calculated
    #     return ''

    def doReadUnit(self):
        return '' if isinstance(self.target, string_types) else 'mrad'

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doWriteCollimation(self, value):
        # TODO: Implement the change of the positions of the NOK's and
        # apertures.
        pass

    # def doReadCollimation(self):
        # TODO: Implement the determination of the collimation depending of the
        # NOK and apertures positions

    def doWritePolarisation(self, value):
        # TODO: Implement the move of the NOK5a, the spin flipper, and the guide
        # field to the corresponding values
        pass

    # def doReadPolarisation(self):
        # TODO: Implement the determination of the polarisation depending of
        # the NOK5a, the spin flipper, and the guide field
