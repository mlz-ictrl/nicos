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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Some convenience classes, methods for NeXus data writing."""

from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXAttribute


seconds = NXAttribute('s', 'string')
counts = NXAttribute('counts', 'string')


def ReactorSource(name, powerdev):
    """Return a typical reactor neutron source structure."""
    return {
        'name': ConstDataset(name, 'string'),
        'type': ConstDataset('Reactor Neutron Source', 'string'),
        'probe': ConstDataset('neutron', 'string'),
        'power': DeviceDataset(powerdev),
        # 'flux': ,
    }


def CounterMonitor(monitor):
    """Return a fission chamber monitor structure."""
    return {
        'mode': ConstDataset('monitor', 'string'),
        'type': ConstDataset('Fission_Chamber', 'string'),
        'preset': DeviceDataset(monitor, 'preselection', dtype='float',
                                units=counts),
        'integral': DetectorDataset(monitor, 'float', units=counts),
    }


def TimerMonitor(timer):
    """Return a timer monitor structure."""
    return {
        'mode': ConstDataset('timer', 'string'),
        'preset': DeviceDataset(timer, 'preselection', dtype='float',
                                units=seconds),
        'integral': DetectorDataset(timer, 'float', units=seconds),
    }
