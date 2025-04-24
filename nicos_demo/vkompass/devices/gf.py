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
# Module author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************


from nicos.core.params import Attach, Override, Param, tupleof
from nicos.devices.generic import VirtualMotor

from nicos_mlz.kompass.devices.gf_lpa import GF_Kompass, GF_Panda


class VectorCoil(VirtualMotor):
    """VectorCoil is a device to control a coil which creates a field at the
    sample position.

    Basically it is a powersupply device, working in Amps and having two
    additional parameters for calibration the vectorfield, for which these
    coil devices are used.
    """

    parameters = {
        'orientation': Param('Field vector which is created by this coil in '
                             'mT (measured value!)',
                             settable=True, default=(1., 1., 1.),
                             type=tupleof(float, float, float), unit='mT',
                             category='general'),
        'calibrationcurrent': Param('Current in A which created the field '
                                    'given as Parameter orientation',
                                    settable=True, default=1., type=float,
                                    unit='A', category='general'),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    def doReadUnit(self):
        return 'A'


class Guidefield4(GF_Kompass):
    attached_devices = {
        'coils': Attach('List of 4 devices used for the vector field',
                        VectorCoil, multiple=4),
    }


class Guidefield3(GF_Panda):
    attached_devices = {
        'coils': Attach('List of 3 devices used for the vector field',
                        VectorCoil, multiple=3),
    }
