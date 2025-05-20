# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@tum.de>
#
# *****************************************************************************

"""NICOS device parameter overrides test suite."""

import pytest

from nicos.core.device import Device
from nicos.core.errors import ProgrammingError
from nicos.core.mixins import DeviceMixinBase
from nicos.core.params import Override, Param


class BlahMixin(DeviceMixinBase):
    """Mixin with a parameter override."""

    parameter_overrides = {
        'blah': Override(volatile=False),
    }


class BlubbMixin(DeviceMixinBase):
    """Mixin with a parameter override."""

    parameter_overrides = {
        'blubb': Override(volatile=False),
    }


class BlahBlubbMixin(BlahMixin, BlubbMixin):
    """Mixin inheriting mixins with parameter overrides."""


# The following classes are defined as good cases for the parameter overrides
class BlahDevice(BlahMixin, Device):
    """Device using a mixin which overrides a parameter."""

    parameters = {
        'blah': Param('...'),
    }


class BlahDevice2(BlahDevice):
    """Device inheriting device inheriting mixin with paramter override."""


class BlubbDevice(BlubbMixin, Device):
    """Device using a mixin which overrides a parameter."""

    parameters = {
        'blubb': Param('...'),
    }


class BlahBlubbDevice(BlahMixin, BlubbMixin, Device):
    """Device inheriting several mixins with parameter overrides."""

    parameters = {
        'blah': Param('...'),
        'blubb': Param('...'),
    }


class BlahBlubbDevice2(BlubbMixin, BlahDevice):
    """Device inheriting mixins and device with parameter overrides."""

    parameters = {
        'blubb': Param('...'),
    }


class BlahBlubDevice3(BlahBlubbMixin, Device):
    """Device inheriting combined mixins with parameter overrides."""

    parameters = {
        'blah': Param('...'),
        'blubb': Param('...'),
    }


class BlubbBlahDevice(BlubbDevice, BlahDevice):
    """Device inheriting several devices with parameter overrides."""


def test_device_overrides_fail():
    """Test for catching missing parameters if override is defined."""
    matchstr = 'contains overrides for non-existing nicos parameters:'
    # No parameter defined for the mixin parameter override
    with pytest.raises(ProgrammingError, match=matchstr):
        type('NoBlahDevice', (BlahMixin, Device),
             {'__module__': 'dummy', '__qualname__': 'NoBlahDevice'})

    # No parameter defined for the mixin parameter override
    with pytest.raises(ProgrammingError, match=matchstr):
        type('NoBlubbDevice', (BlubbMixin, BlahDevice),
             {'__module__': 'dummy', '__qualname__': 'NoBlubbDevice'})

    # There is a parameter override defined but the parameter is missing
    with pytest.raises(ProgrammingError, match=matchstr):
        type('NoParamDevice', (Device, ),
             {'__module__': 'dummy', '__qualname__': 'NoParamDevice',
              'parameter_overrides': {'noparam': Override(type=float)}})
