# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""VRefsans detector image based on McSTAS simulation."""

import numpy as np

from nicos.core import Attach, Override, Param, Readable, oneof
from nicos.core.constants import FINAL, LIVE
from nicos.devices.mcstas import McStasImage as BaseImage, \
    McStasSimulation as BaseSimulation


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='MLZ_SANS_1'),
    }

    parameters = {
        'gravity': Param('Switch the gravity on/off',
                         type=bool, settable=True, mandatory=False,
                         default=True),
    }

    attached_devices = {
        'wl': Attach('Wavelength', Readable),
        'dlambda': Attach('Wavelength spread', Readable),
        'nose_slit': Attach('Circular slit at nose', Readable),
        'sd': Attach('Sample detector distance', Readable),
        'coll': Attach('Collimation', Readable),
        'tilt': Attach('Selector tilt angle', Readable),
        'det1rot': Attach('Primary detector rotation', Readable),
        'det1x': Attach('Primary detector x position', Readable),
        'samplepos': Attach('Sample X position', Readable),
        'sword': Attach('Sword device', Readable),
    }

    # noCS          []      with (0) or without cold source (1)
    # tofMode       []      none (0) or include time-of-flight with old disk
    #                       (1) or new (2, strongly recommended)
    # Lam           [A]     central wavelength
    # dLam          [A]     +/- delta lambda
    # mL            []      m-value outer horizontal side second part S-bender
    #                       section [1]
    # mR            []      m-value inner sides S-Bender section [1]
    # nhS           []      number of horizontal channels in s-bender [1]
    # tilt          [deg]   tilt angle of selector
    # newSel        []      whether to use the new selector (1) or not (0)
    # sLam          [A]     set the selector wavelength
    # disFreq       [Hz]    set the rotations per seconds of chopper disk
    # pol_pos       [0]     0=guide, 1=2700mm polarizer, 2=1500mm polarizer
    # CD            [m]     collimation distance in meters [2, 4, 8, 12, 16, 20]
    # ap_wheel_1    []      variable aperture, 1=51mm square, 2=50mm circular,
    #                       3=42mm circular, 4=20mm circular
    # ap_wheel_2    []      variable aperture, 1=51mm square, 2=30mm circular,
    #                       3=20mm circular, 4=12mm circular
    # sword         []      variable aperture, 1=51mm square, 2=30mm circular,
    #                       3=20mm circular, 4=10mm circular
    # nose_sslit    [mm]    variable circular slit, diameter
    # sample_pos    [m]     position of sample from "origin", [m]
    # sample_type   []      whether to use an incoherent scatterer [0] or the
    #                       custom Diff+SANS sample [1]
    # nose_sam      []      which nose to use after sample or no nose
    #                       [0, 1, 2, 3, 4 (recommended)]
    # SD            [m]     Sample Detector distance
    # Dx            [m]     Horizontal offset from beam center, max 0.5
    # Turn          [deg]   Turn of primary detector
    # virtNameSel   []      name of the virtual source, at selector entry
    #
    # --- SET TO STANDARD VALUES ---
    # SD2T          [m]     Top Second Detector distance in ->
    #                       Standard [1.5] + 0.008619
    # Dx2T          [m]     Horizontal offset from beam center,
    #                       default is as center of beam tube
    # Dy2T          [m]     Vertical offset from beam center,
    #                       default at border of beam tube -> 0.8132
    # Turn2T        [deg]   Turn of second detector along horiz. axis -> -20
    # SD2B          [m]     Bottom Second Detector distance in ->
    #                       Standard [1.5]+ 0.00643
    # Dx2B          [m]     Horizontal offset from beam center,
    #                       default is as center of beam tube
    # Dy2B          [m]     Vertical offset from beam center,
    #                       default at border of beam tube -> 0.63334
    # Turn2B        [deg]   Turn of second detector along horiz. axis -> 20
    # SD2S          [m]     Side Second Detector distance in ->
    #                       Standard [1.0] + 0.11441
    # Dx2S          [m]     Horizontal offset from beam center,
    #                       default to border of beam tube -> -1.1254
    # Turn2S        [deg]   Turn of second detector along vert. axis -> -27

    def _prepare_params(self):
        # pylint: disable=line-too-long
        params = []
        if self.gravity:
            params.append('-g')  # Switch gravitation on
        params.extend([
            'tofMode=0',
            'Lam=%s' % self._dev_value(self._attached_wl),
            'tilt=%s' % self._dev_value(self._attached_tilt),
            'CD=%s' % self._dev_value(self._attached_coll),
            'Turn=%s' % self._dev_value(self._attached_det1rot),
            'Dx=%s' % self._dev_value(self._attached_det1x, 1000),
            'nose_sslit=%s' % self._dev_value(self._attached_nose_slit),
            'SD=%s' % self._dev_value(self._attached_sd, 1000),
            'ap_wheel_1=%s' % '1',  # variable aperture, 1= 51mm square, 2=50mm circular, 3=42mm circular, 4=20mm circular =bg1
            'ap_wheel_2=%s' % '1',  # variable aperture, 1= 51mm square, 2=30mm circular, 3=20mm circular, 4=12mm circular=bg2
            'sword=%s' % self._dev_value(self._attached_sword),  # variable aperture, 1= 51mm square, 2=30mm circular, 3=20mm circular, 4=10mm circular=sa1
            'sample_pos=%s' % self._dev_value(self._attached_samplepos, 1000),
            # x Lam= lambda
            # ap_wheel_1: variable aperture, 1= 51mm square, 2=50mm circular, 3=42mm circular, 4=20mm circular = bg1
            # ap_wheel_2: variable aperture, 1= 51mm square, 2=30mm circular, 3=20mm circular, 4=12mm circular = bg2
            # sword: variable aperture, 1= 51mm square, 2=30mm circular, 3=20mm circular, 4=10mm circular = sa1
            # x nose_slit: variable circular slit, diameter in [mm] = gibt es nur als virtuelle Achse sa2 im Nicos, Probenblende per Hand gesetzt
            # x sample_pos: position of sample from "origin", [m], entspricht in etwa st1_x, brauchen wir aber eigentlich im virtuellen Instrument nicht.
            # x SD: Sample Detector distance in [m]=det1_z
            # x Dx: Horizontal offset from beam center, max 0.5 [m]=det1_x
            # x Turn: Turn of primary detector [deg] = det1_omg
            # x CD: collimation distance in metre [2, 4, 8, 12, 16, 20]=col
        ])
        dl = self._attached_wl.read(0) * abs(self._attached_dlambda.read(0)) / 100
        params.append(
            'dLam=%s' % self._attached_wl.format(dl)
        )
        return params


class McStasImage(BaseImage):

    parameters = {
        'neutron_section': Param("Section to take 'neutrons' from PSD file",
                                 type=oneof('Data', 'Events'), mandatory=False,
                                 default='Events'),
    }

    def _readpsd(self, quality):
        if self._attached_mcstas._signal_sent or quality == FINAL:
            try:
                blocks = 1 if self.neutron_section == 'Events' else 3
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    lines = f.readlines()[-blocks * (self.size[1] + 1):]
                if lines[0].startswith(f'# {self.neutron_section}') and \
                   self.mcstasfile in lines[0]:
                    factor = 1 if blocks == 1 else self._attached_mcstas._getScaleFactor()
                    buf = factor * np.loadtxt(lines[1:self.size[1] + 1],
                                              dtype=np.float32)
                    self._buf = buf.astype(self.image_data_type)
                    self.readresult = [self._buf.sum()]
                    self.log.debug('Read result: %s', self.readresult)
                elif quality != LIVE:
                    raise OSError('Did not find start line: %s' % lines[0])
            except OSError:
                if quality != LIVE:
                    self.log.exception('Could not read result file', exc=1)
        else:
            self.readresult = [0]
            self._buf = np.zeros(self.size).astype(self.image_data_type)
