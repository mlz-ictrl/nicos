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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""SANS1 resolution device."""

from nicos.core.device import Readable
from nicos.core.params import Attach, Override

from nicos_mlz.sans1.devices.beamstop import BeamStop
from nicos_mlz.sans1.devices.detector import Detector
from nicos_mlz.sans1.lib import qrange


class Resolution(Readable):

    valuetype = (float, float)

    attached_devices = {
        'detector': Attach('Detector device with size information',
                           Detector),
        'beamstop': Attach('Beam stop device with size information',
                           BeamStop),
        'detpos': Attach('Detector position device', Readable),
        'wavelength': Attach('Wavelength device', Readable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
        'fmtstr': Override(default='%3.f - %3.f'),
    }

    def doRead(self, maxage=0):
        bs = self._attached_beamstop
        return qrange(self._attached_wavelength.read(maxage),
                      self._attached_detpos.read(0),
                      bs.slots[bs.shape][1][0] / 2.,
                      self._attached_detector.size[0] / 2.)

    def doReadUnit(self):
        unit = self._attached_wavelength.unit
        return '%s-1' % unit
