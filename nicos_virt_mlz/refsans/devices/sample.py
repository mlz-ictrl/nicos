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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Virtual Refsans specific sample implementation."""

from nicos.core.params import Param, Override, absolute_path

from nicos_mlz.refsans.devices.sample import Sample as BaseSample


class Sample(BaseSample):
    """Virtual Refsans specific sample."""

    parameters = {
        'sample_file': Param('Sample definition file',
                             type=str, settable=True, userparam=True,
                             default='Si_Ti_Al_Mirror.dat'),
        'datapath': Param('Path to the sample definition files',
                          type=absolute_path, settable=False, userparam=True,
                          default='/tmp'),
    }

    parameter_overrides = {
        'samples': Override(mandatory=True, settable=False, internal=False),
    }

    def _applyParams(self, number, parameters):
        BaseSample._applyParams(self, number, parameters)
        for key, value in parameters.items():
            if key in ['sample_file', 'datapath']:
                setattr(self, key, value)
