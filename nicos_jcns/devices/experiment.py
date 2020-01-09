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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""NICOS experiment device with support of IFF sample database"""

from __future__ import absolute_import, division, print_function

from nicos.core import Attach, Param
from nicos.devices.experiment import Experiment as BaseExperiment

from nicos_jcns.devices.sample import Sample


class Experiment(BaseExperiment):
    """Experiment device that requires a sample device with a valid IFF sample
    database ID.
    """

    parameters = {
        'sampledb_botname': Param(
            'Name of the IFF sample database bot user used in the keystore.',
            type=str,
            default='nicos',
            internal=True,
        ),
        'sampledb_url': Param(
            'URL of the IFF sample database.',
            type=str,
            # TODO: default='https://iffsamples.fz-juelich.de/api/v1/'
            default='https://docker.iff.kfa-juelich.de/dev-sampledb/api/v1/',
            internal=True,
        ),
    }

    attached_devices = {
        'sample': Attach(
            'The device object representing the sample with a valid IFF '
            'sample database ID.',
            Sample,
        ),
    }
