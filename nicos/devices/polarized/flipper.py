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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Spin flipper classes."""

from nicos.core import Moveable, Param, Override, oneof, tupleof, multiStop, \
    nonemptylistof, Attach

ON = 'on'
OFF = 'off'


class BaseFlipper(Moveable):
    """
    Base class for a flipper device, which can be moved "on" and "off".
    """

    hardware_access = False

    attached_devices = {
        'flip': Attach('flipping current', Moveable),
        'corr': Attach('correction current, compensating the ext. field', Moveable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = oneof(ON, OFF)

    def doRead(self, maxage=0):
        if abs(self._attached_corr.read(maxage)) > 0.05:
            return ON
        return OFF


class MezeiFlipper(BaseFlipper):
    """
    Class for a Mezei type flipper consisting of flipper and correction current.

    For the state "on" the two power supplies are moved to the values given by
    the `currents` parameter, for "off" they are moved to zero.
    """

    parameters = {
        'currents': Param('Flipper and correction current', settable=True,
                          type=tupleof(float, float)),
    }

    def doStart(self, value):
        if value == ON:
            self._attached_flip.start(self.currents[0])
            self._attached_corr.start(self.currents[1])
        else:
            self._attached_flip.start(0)
            self._attached_corr.start(0)


class KFlipper(BaseFlipper):
    """
    Class for an momentum dependent type flipper consisting of flipper and correction field.

    So far only used at PANDA, but would work on other TAS-like instruments.
    For the state "on" the two power supplies are moved to the values calculated
    from the `flipcurrent` parameter and the value of the `compcurrent`,
    for "off" they are moved to zero.
    The current neutron momentum is read from a `wavevector` device which
    should be attached to the relevant monochromator/analyser,
    depending on the location of the spinflipper.
    """
    attached_devices = {
        'kvalue': Attach('Device reading current k value, needed for '
                         'calculation of flipping current.', Moveable),
    }

    parameters = {
        'compcurrent': Param('Current in A for the compensation coils, if active',
                             settable=True, type=float, unit='A'),
        'flipcurrent': Param('Polynomial in wavevector to calculate the '
                             'correct flipping current',
                             settable=True, type=nonemptylistof(float),
                             unit='A'),  # actually A * Angstroms ** index
    }

    def doStart(self, value):
        if value == ON:
            # query current momentum and calculate polinomial
            k = self._attached_kvalue.read(0)
            flip_current = sum(v * (k ** i) for i, v in enumerate(self.flipcurrent))
            self._attached_flip.start(flip_current)
            self._attached_corr.start(self.compcurrent)
        else:
            self._attached_flip.start(0)
            self._attached_corr.start(0)

    def doStop(self):
        # doStop needs to be implemented this way to not stop the kvalue device!
        multiStop((self.field, self.compensate))
