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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS specific McStas devices."""

import numpy as np

from nicos import session
from nicos.core import ArrayDesc, Override, Param, listof, oneof
from nicos.devices.mcstas import DetectorMixin, McStasImage, McStasSimulation

from nicos_mlz.kws1.devices.daq import RTMODES, KWSDetector


class KwsSimulation(McStasSimulation):

    parameter_overrides = {
        'mcstasprog': Override(default='KWS1gisans'),
        'neutronspersec': Override(default={'localhost': 2.5e5}),
    }

    def _prepare_params(self):
        def param(mcstas, nicos=None, f=lambda x: x):
            val = session.getDevice(nicos or mcstas).read(0)
            return '%s=%s' % (mcstas, f(val))
        mm2m = lambda x: x/1000  # pylint: disable=unnecessary-lambda-assignment
        coll_d = session.getDevice('coll_guides').read(0)

        return [
            param('Lam', 'selector_lambda'),
            'sel_ang=0',
            param('Clen', 'coll_guides'),
            param('Dlen', 'det_z'),
            param('smpx', 'sam_trans_x', mm2m),
            param('smpy', 'sam_trans_y', mm2m),
            param('cslitw', 'aperture_%02d' % coll_d, lambda x: x[0] / 1000),
            param('cslith', 'aperture_%02d' % coll_d, lambda x: x[1] / 1000),
            param('sslitw', 'ap_sam.width', mm2m),
            param('sslith', 'ap_sam.height', mm2m),
            param('sslitx', 'ap_sam.centerx', mm2m),
            param('sslity', 'ap_sam.centery', mm2m),
            param('bx', 'beamstop_x', mm2m),
            param('by', 'beamstop_y', lambda x: x / 1000 - 0.52),
            'vheight=0',
        ]


class KwsDetectorImage(McStasImage):

    parameters = {
        'mode':   Param('Measurement mode switch', type=oneof(*RTMODES),
                        settable=True, category='general'),
        'slices': Param('Calculated TOF slices', internal=True,
                        unit='us', settable=True, type=listof(int),
                        category='general'),
        'rebin8x8': Param('Rebin data to 8x8 mm pixel size', type=bool,
                          default=False, settable=True, mandatory=False),
    }

    def _configure(self, tofsettings):
        if self.mode == 'standard':
            self.slices = []
            self.arraydesc = ArrayDesc(self.name, self.size[::-1], np.uint32)
        else:
            # set timing of TOF slices
            channels, interval, q, custom = tofsettings
            if custom:
                if custom[0] != 0:
                    custom = [0] + custom
                times = custom
            else:
                times = [0]
                for i in range(channels):
                    times.append(times[-1] + int(interval * q**i))
            self.slices = times
            self.arraydesc = ArrayDesc(
                self.name, (channels, self.size[1], self.size[0]), np.uint32)

    def doReadArray(self, quality):
        # TODO: non-standard modes
        res = McStasImage.doReadArray(self, quality)
        if self.rebin8x8:
            res = res[::2, :] + res[1::2, :]  # add up bins
            res = np.pad(res, ((64, 64), (0, 0)), mode='constant')
        if self.mode != 'standard':
            return np.repeat([res], len(self.slices) - 1, 0)
        return res


class Detector(DetectorMixin, KWSDetector):
    pass
