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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Standin motors for virtual instrument setups."""

from __future__ import absolute_import, division, print_function

from nicos.core import HasPrecision, Override, status
from nicos.devices.generic.manual import ManualMove, ManualSwitch


class Standin(HasPrecision, ManualMove):
    """Override to always return a warning state, and not require
    parameters that are already set in the non-virtual setup.
    """

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
        'unit':      Override(mandatory=False),
    }

    def doStatus(self, maxage=0):
        return status.WARN, 'virtual'


class NonvirtualStandin(HasPrecision, ManualMove):
    parameter_overrides = {
        'abslimits': Override(mandatory=False),
        'unit':      Override(mandatory=False),
    }


class StandinSwitch(ManualSwitch):
    """Override to always return a warning state."""

    def doStatus(self, maxage=0):
        sc, _ = ManualSwitch.doStatus(self, maxage)
        if sc == status.OK:
            sc = status.WARN
        return sc, 'virtual'
