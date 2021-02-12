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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""VPANDA specific McStas devices."""

from nicos import session
from nicos.core import Override

from nicos.devices.mcstas import McStasSimulation


class PandaSimulation(McStasSimulation):

    parameter_overrides = {
        'mcstasprog': Override(default='vpanda'),
        'mcstasfile': Override(default='PSD_det.psd'),
    }

    def _prepare_params(self):
        def param(mcstas, nicos=None, f=lambda x: x):
            val = session.getDevice(nicos or mcstas).read(0)
            return '%s=%s' % (mcstas, f(val))
        scatsense = session.getDevice('panda').scatteringsense
        mm2m = lambda x: x/1000

        return [
            'prim_shut_pos=1',
            param('sapphire', 'saph', f=lambda x: 1 if x == 'in' else 0),
            param('ca1', f=lambda x: x.strip('m') if x != 'none' else 120),
            param('ca2', f=lambda x: x.strip('m') if x != 'none' else 120),
            param('ca3', f=lambda x: x.strip('m') if x != 'none' else 120),
            param('ca4', f=lambda x: x.strip('m') if x != 'none' else 120),
            param('ms1', f=mm2m),
            param('lms', f=mm2m),
            param('lsa', f=mm2m),
            param('lad', f=mm2m),
            'ki=0',
            'kf=0',
            'dE=0',
            'Q=0',
            param('mth', f=lambda x: -x),  # negate due to coupled axis
            param('mtt'),
            param('mtx', f=mm2m),
            param('mty', f=mm2m),
            'mgy=0',
            param('mfh'),
            param('mfv'),
            'scatsense_mono=%d' % scatsense[0],
            'scatsense_sample=%d' % scatsense[1],
            'scatsense_ana=%d' % scatsense[2],
            param('sth'),
            param('stt'),
            param('stx', f=mm2m),
            param('sty', f=mm2m),
            param('stz', f=mm2m),
            param('sgx'),
            param('sgy'),
            param('ss1_width',  'ss1.width',  f=mm2m),
            param('ss1_height', 'ss1.height', f=mm2m),
            param('ss2_width',  'ss2.width',  f=mm2m),
            param('ss2_height', 'ss2.height', f=mm2m),
            param('ath'),
            param('att'),
            'atx=0',
            param('aty', f=mm2m),
            'agy=0',  # TODO: we have agx not agy...
            param('afh'),
            'afv=0.6',
        ]
