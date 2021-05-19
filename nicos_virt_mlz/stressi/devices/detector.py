#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""VStressi detector image based on McSTAS simulation."""

from nicos.core import Attach, Override, Readable
from nicos.devices.mcstas import McStasSimulation as BaseSimulation

from nicos_virt_mlz.stressi.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'size': Override(default=(256, 256)),
        'mcstasprog': Override(default='stressi_fast'),
        'mcstasfile': Override(default='PSD_STRESSI_total.psd'),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'xprime': Attach('Primary slit width', Readable),
        'yprime': Attach('Primary slit height', Readable),
        'l_ambda': Attach('Wave length', Readable),
        'xpos': Attach('Sample position x', Readable),
        'ypos': Attach('Sample position y', Readable),
        'zpos': Attach('Sample position z', Readable),
        'phi': Attach('Sample phi rotation', Readable),
        'chi': Attach('Sample chi rotation', Readable),
        'omega': Attach('Sample omega rotation', Readable),
        'theta2': Attach('Rotation of detector around the sample', Readable),
        'force': Attach('Force of the tensile rig', Readable, optional=True),
    }

    def _dev(self, dev, scale=1):
        return dev.fmtstr % (dev.read(0) / scale)

    def _prepare_params(self):
        return [
            'xprime=%s' % self._dev(self._attached_xprime, 2 * 1000),
            'yprime=%s' % self._dev(self._attached_yprime, 2 * 1000),
            'primeswitch=1',
            'lambda=%s' % self._dev(self._attached_l_ambda),
            'xpos=%s' % self._dev(self._attached_xpos, 1000),
            'ypos=%s' % self._dev(self._attached_ypos, 1000),
            'zpos=%s' % self._dev(self._attached_zpos, 1000),
            'phi=%s' % self._dev(self._attached_phi),
            'chi=%s' % self._dev(self._attached_chi),
            'omega=%s' % self._dev(self._attached_omega),
            'theta2=%s' % self._dev(self._attached_theta2),
            'force=%s' % (self._dev(self._attachec_force)
                          if self._attached_force else 0),
            'sampleswitch=%d' % self._attached_sample.sampletype,
        ]
