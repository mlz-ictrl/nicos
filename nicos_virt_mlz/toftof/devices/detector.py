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

"""VTOFTOF detector image based on McSTAS simulation."""

import re
from math import log10

from nicos.core import Attach, Override, Param, intrange
from nicos.devices.generic.slit import Slit
from nicos.devices.mcstas import DetectorMixin, McStasImage, \
    McStasSimulation as BaseSimulation

from nicos_mlz.toftof.devices import Detector as BaseDetector, Ratio, \
    SlitType, Speed, Wavelength
from nicos_virt_mlz.toftof.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='TOFTOF_NICOS'),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'wavelength': Attach('Wave length device', Wavelength),
        'speed': Attach('Chopper rotation speed device', Speed),
        'ratio': Attach('Chopper disc ratio device', Ratio),
        'st': Attach('Chopper slit type', SlitType),
        'slit': Attach('Sample slit', Slit),
    }

    def _dev(self, dev, scale=1, default='0', fmtstr=None):
        if not dev:
            return default
        if not fmtstr:
            fmtstr = dev.fmtstr
        if scale > 1:
            sf = int(log10(scale))
            expr = re.compile(r'(?<=\.)\d+')
            nums = re.findall(expr, fmtstr)
            if nums:
                num = int(nums[0]) + sf
                m = re.search(expr, fmtstr)
                fmtstr = '%s%d%s' % (fmtstr[:m.start()], num, fmtstr[m.end()])
        return fmtstr % (dev.read(0) / scale)

    # lambda:      [AA]     observation wavelength
    # speed:       [rpm]    chopper speed (60 * frequency)
    # ratio:       [1]      every [1] puls will pass the 5 frame overlap
    #                       chopper (FO)
    # chST:        [1]      0 for wide chopper slits,
    #                       1 for small chopper slits,
    #                       2 for wide slits on chopper 1 and 6 and small slits
    #                       for chopper 2 and 7
    # focused_beam [1]      Use 0 for linear guide and 1 for focusing guides
    # Ah, Aw:      [m]      Height and width of focussing guide at the exit
    # slits_hor    [mm]     Horizontal slit width
    # slits_vert   [mm]     Vertical slit width
    # sample       [1]      0 = Vanadium, 1 = empty cell, 2 = water
	# scat_order   [1]		Limit multiple scattering up to given order
    #                       0 = all, 1 = single, 2 = double, ...
    # repeat       [1]      repetition of the neutrons from the virtual source
    # split_var    [1]      repetition of the neutrons arriving in front of the
    #                       sample

    def _prepare_params(self):
        return [
            'lambda=%s' % self._dev(self._attached_wavelength),  # 6
            'speed=%s' % self._dev(self._attached_speed),  # 14000
            # chopper definitions
            'ratio=%s' % self._dev(self._attached_ratio),  # 2
            'chST=%s' % self._dev(self._attached_st),  # 0
            'focused_beam=%d' % 0,  # focussed beam
            # slits in mm
            'slits_hor=%s' % self._dev(self._attached_slit.width),
            'slits_vert=%s' % self._dev(self._attached_slit.height),
            # 0 = Vanadium, 1 = empty cell, 2 = water
            'sample=%d' % self._attached_sample.sampletype,
            'scat_order=%d' % 0,
            'repeat=%d' % 1000,
            'split_var=%d' % 1000,
        ]


class Image(McStasImage):

    parameters = {
        'timechannels': Param('Number of time channels per detector channel',
                              type=intrange(1, 4096), settable=True,
                              default=1024, category='general'),
        'frametime': Param('Time interval between pulses',
                           type=float, settable=True,
                           default=0.0128571, unit='s',
                           category='general',
                           ),
        'delay': Param('TOF frame delay',
                       type=float, settable=True,
                       default=162093*5e-8, fmtstr='%g', unit='s',
                       category='general',
                       ),
        'timeinterval': Param('Duration of a single time slot',
                              default=252*5e-8, unit='s',
                              category='general',
                              ),
    }


class Detector(DetectorMixin, BaseDetector):
    """Detector subclass for McStas simulations that don't require a custom
    Detector class.
    """
