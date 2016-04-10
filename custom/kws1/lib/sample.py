#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""KWS sample object."""

from nicos import session
from nicos.core import Param, dictof, tupleof, anytype, multiWait, \
    ConfigurationError
from nicos.frm2.sample import Sample


class KWSSample(Sample):
    """Device that collects the various sample properties specific to
    samples at KWS.
    """

    parameters = {
        'aperture':   Param('Aperture (x, y, w, h) for position',
                            type=tupleof(float, float, float, float),
                            unit='mm', settable=True),
        'position':   Param('Mapping of devices to positions for driving '
                            'to this sample\'s position',
                            type=dictof(str, anytype), settable=True),
        'timefactor': Param('Measurement time factor for this sample',
                            type=float, settable=True),
        'thickness':  Param('Sample thickness (info only)',
                            type=float, settable=True, unit='mm'),
        'detoffset':  Param('Detector offset (info only)',
                            type=float, settable=True, unit='mm'),
        'comment':    Param('Sample comment',
                            type=str, settable=True),
    }

    def _applyKwsParams(self, parameters):
        # these keys must be present when dealing with KWS1 samples, but are
        # *not* present in the dummy sample created on experiment start
        self.aperture = parameters.get('aperture', (0.0, 0.0, 20.0, 20.0))
        self.position = parameters.get('position', {})
        self.timefactor = parameters.get('timefactor', 1.0)
        self.thickness = parameters.get('thickness', 0.0)
        self.detoffset = parameters.get('detoffset', 0.0)
        self.comment = parameters.get('comment', '')

    def clear(self):
        Sample.clear(self)
        self._applyKwsParams({})

    def _applyParams(self, number, parameters):
        Sample._applyParams(self, number, parameters)
        self._applyKwsParams(parameters)

        self.log.info('moving to position of sample %s (%s)...' %
                      (number, parameters['name']))
        ap = session.getDevice('ap_sam')
        ap.opmode = 'offcentered'  # to be sure
        ap.move(self.aperture)
        waitdevs = [ap]
        for devname, devpos in self.position.iteritems():
            dev = session.getDevice(devname)
            dev.move(devpos)
            waitdevs.append(dev)
        multiWait(waitdevs)

    def set(self, number, parameters):
        for key in ('name', 'aperture', 'position', 'timefactor',
                    'thickness', 'detoffset', 'comment'):
            if key not in parameters:
                raise ConfigurationError(self, 'missing key %r in sample entry'
                                         % key)
        Sample.set(self, number, parameters)
