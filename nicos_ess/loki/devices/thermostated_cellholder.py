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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""LoKI thermostated cell-holder device."""
from nicos import session
from nicos.core import POLLER, Attach, LimitError, Moveable, Override, Param, \
    anytype, dictof, listof, tupleof
from nicos.devices.abstract import MappedMoveable
from nicos.devices.generic import MultiSwitcher


class ThermoStatedCellHolder(MultiSwitcher):
    """The thermostated cell-holder device."""
    parameters = {
        'cartridges':
            Param('Cartridge configurations '
                  '(top-left to bottom-right)',
                  type=listof(dictof(str, anytype)),
                  userparam=False,
                  settable=True,
                  default=[{}, {}, {}, {}, {}, {}]),
        'cell_spacings':
            Param('The horizontal distance between cell centres',
                  type=dictof(str, int),
                  userparam=False,
                  unit='mm',
                  default={
                      'narrow': 20,
                      'wide': 10,
                      'rotation': 40,
                  }),
        'number_cells':
            Param('The number of cells for the cartridge type',
                  type=dictof(str, int),
                  userparam=False,
                  default={
                      'narrow': 8,
                      'wide': 4,
                      'rotation': 6,
                  }),
        'xlimits':
            Param('The limits of the x-axis motor',
                  type=tupleof(float, float),
                  volatile=True,
                  userparam=False,
                  settable=False),
        'ylimits':
            Param('The limits of the y-axis motor',
                  type=tupleof(float, float),
                  volatile=True,
                  userparam=False,
                  settable=False)
    }

    parameter_overrides = {
        'mapping':
            Override(description='Cell position to motor positions',
                     mandatory=False,
                     userparam=False,
                     settable=True,
                     type=dictof(str, tupleof(float, float))),
    }

    attached_devices = {
        'moveables':
            Attach('The motors for positioning the cells',
                   Moveable,
                   multiple=2,
                   optional=True),
        'ymotor':
            Attach('The vertical positioning motor', Moveable),
        'xmotor':
            Attach('The horizontal positioning motor', Moveable),
    }

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)
        if session.sessiontype != POLLER:
            self._generate_mapping(self.cartridges)
        self._attached_moveables = [
            self._attached_xmotor, self._attached_ymotor
        ]

    def doReadXlimits(self):
        return self._attached_xmotor.userlimits

    def doReadYlimits(self):
        return self._attached_ymotor.userlimits

    def doWriteMapping(self, mapping):
        for position in mapping.values():
            self._check_limits(position)

    def _generate_mapping(self, cartridges):
        new_mapping = {}

        for cartridge in cartridges:
            labels = cartridge.get('labels', [])
            positions = cartridge.get('positions', [])
            for label, position in zip(labels, positions):
                new_mapping[label] = position
        self.mapping = new_mapping

    def doWriteCartridges(self, cartridges):
        self._generate_mapping(cartridges)

    def _check_limits(self, position):
        x, y = position
        xlimits = self._attached_xmotor.userlimits
        if x < xlimits[0] or x > xlimits[1]:
            raise LimitError(
                f'cartridge x position ({x}) outside motor limits '
                f'({xlimits})')

        ylimits = self._attached_ymotor.userlimits
        if y < ylimits[0] or y > ylimits[1]:
            raise LimitError(
                f'cartridge y position ({y}) outside motor limits '
                f'({ylimits})')
