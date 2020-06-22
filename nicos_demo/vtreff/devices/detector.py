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

"""VTREFF detector image based on McSTAS simulation."""

from __future__ import absolute_import, division, print_function

from nicos.core import Attach, Override, Readable
from nicos.devices.generic import Slit

from nicos_demo.devices import McStasImage as BaseImage
from nicos_mlz.treff.devices import MirrorSample


class McStasImage(BaseImage):

    parameter_overrides = {
        'size': Override(default=(256, 256)),
        'mcstasprog': Override(default='treff_fast'),
        'mcstasfile': Override(default='PSD_TREFF_total.psd'),
    }

    attached_devices = {
        'sample': Attach('Mirror sample', MirrorSample),
        's1': Attach('Slit 1', Slit),
        's2': Attach('Slit 2', Slit),
        'sample_x': Attach('Sample position x', Readable),
        'sample_y': Attach('Sample position y', Readable),
        'sample_z': Attach('Sample position z', Readable),
        'beamstop': Attach('Beam stop positon', Readable),
        'omega': Attach('Sample omega rotation', Readable),
        'chi': Attach('Sample chi rotation', Readable),
        'phi': Attach('Sample phi rotation', Readable),
        'detarm': Attach('Position detector arm', Readable),
    }

    def _prepare_params(self):
        params = []
        sample = self._attached_sample
        params.append('s1_width=%s' % self._attached_s1.width.read(0))
        params.append('s1_height=%s' % self._attached_s1.height.read(0))
        params.append('s2_width=%s' % self._attached_s2.width.read(0))
        params.append('s2_height=%s' % self._attached_s2.height.read(0))
        params.append('sample_x=%s' % self._attached_sample_x.read(0))
        sample_y = self._attached_sample_y
        params.append('sample_y=%s' % (sample_y.read(0) + sample_y.offset +
                                       sample._misalignments['sample_y']))
        params.append('sample_z=%s' % self._attached_sample_z.read(0))
        params.append('beamstop_pos=%s' % self._attached_beamstop.read(0))
        omega = self._attached_omega
        params.append('omega=%s' % (
            omega.read(0) + omega.offset + sample._misalignments['omega']))
        chi = self._attached_chi
        params.append('chi=%s' % (
            chi.read(0) + chi.offset + sample._misalignments['chi']))
        params.append('phi=%s' % self._attached_phi.read(0))
        detarm = self._attached_detarm
        params.append('detarm=%s' % (
            detarm.read(0) + detarm.offset + sample._misalignments['detarm']))
        params.append('mirror_length=%s' % self._attached_sample.length)
        params.append('mirror_thickness=%s' % self._attached_sample.thickness)
        params.append('mirror_height=%s' % self._attached_sample.height)
        params.append('mirror_m=%s' % self._attached_sample.m)
        params.append('mirror_alfa=%s' % self._attached_sample.alfa)
        params.append('mirror_wav=%s' % self._attached_sample.waviness)
        if self._attached_sample.rflfile:
            params.append('rflfile=%s' % self._attached_sample.rflfile)
        else:
            params.append('rflfile=0')
        return params
