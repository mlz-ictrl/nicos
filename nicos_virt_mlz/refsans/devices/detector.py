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

"""VRefsans detector image based on McSTAS simulation."""

import os
import re
from math import log10

from nicos.core import Attach, Param, Override, Readable
from nicos.devices.mcstas import McStasSimulation as BaseSimulation
from nicos.devices.generic import HorizontalGap

from nicos_mlz.refsans.devices.chopper.base import ChopperDisc
from nicos_mlz.refsans.devices.nok_support import DoubleMotorNOK
from nicos_mlz.refsans.devices.sample import Sample
from nicos_mlz.refsans.devices.slits import DoubleSlit, SingleSlit


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='REFSANS_NICOS'),
    }

    parameters = {
        'gravity': Param('Switch the gravity on/off',
                         type=bool, settable=True, mandatory=False,
                         default=True),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'zb0': Attach('Slit ZB0', SingleSlit),
        'zb1': Attach('Slit ZB0', SingleSlit),
        'zb2': Attach('Slit ZB0', SingleSlit),
        'zb3': Attach('Slit ZB3', DoubleSlit),
        'bs1': Attach('Slit BS1', DoubleSlit),
        'b1': Attach('Slit B1', DoubleSlit),
        'b2': Attach('Slit B2', DoubleSlit),
        'h2': Attach('Slit H2', HorizontalGap),
        'b3': Attach('Slit B3', DoubleSlit),
        'h3': Attach('Slit H3', DoubleSlit),
        'gonio_theta': Attach('Goniometer (theta)', Readable),
        'gonio_y': Attach('Goniometer (y)', Readable),
        'gonio_z': Attach('Goniometer (z)', Readable),
        'gonio_top_z': Attach('Top goniometer (z)', Readable,
                              optional=True),
        'pivot': Attach('Pivot point of the detector', Readable),
        'rpm': Attach('Chopper speed', Readable),
        'disc2_pos': Attach('Position of the chopper disc 2', Readable),
        'backguard': Attach('Backguard', Readable),
        'yoke': Attach('Yoke', Readable),
        'dettable': Attach('Detector table', Readable),
        'chopper2': Attach('Chopper disc 2', ChopperDisc),
        'chopper3': Attach('Chopper disc 3', ChopperDisc),
        'chopper4': Attach('Chopper disc 4', ChopperDisc),
        'chopper5': Attach('Chopper disc 5', ChopperDisc),
        'chopper6': Attach('Chopper disc 6', ChopperDisc),
        'nok2': Attach('NOK 2', DoubleMotorNOK),
        'nok3': Attach('NOK 3', DoubleMotorNOK),
        'nok4': Attach('NOK 4', DoubleMotorNOK),
        'nok5a': Attach('NOK 5a', DoubleMotorNOK),
        'nok5b': Attach('NOK 5b', DoubleMotorNOK),
        'nok6': Attach('NOK 6', DoubleMotorNOK),
        'nok7': Attach('NOK 7', DoubleMotorNOK),
        'nok8': Attach('NOK 8', DoubleMotorNOK),
        'nok9': Attach('NOK 9', DoubleMotorNOK),
        'd_b3_sample': Attach('Distance B3 to sample', Readable),
        'det_table': Attach('Detector table position', Readable),
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

    # sim_chopper []      A flag to use (1) or not (0) the chopping system,
    #                     useful to speedup the simulation
    # rpm         [1/min] Rotational speed of chopper disks
    #                     (ignored if sim_chopper = 0)
    # disc2_Pos   [1]     Real Position of disc2 (1-5)
    #                     (ignored if sim_chopper = 0)
    # angle2      [deg]   Real phase value of disc2 relative to disc1
    #                     (master chopper) (ignored if sim_chopper = 0)
    # angle3      [deg]   Real phase value of disc3 relative to disc1
    #                     (ignored if sim_chopper = 0)
    # angle4      [deg]   Real phase value of disc4 relative to disc1
    #                     (ignored if sim_chopper = 0)
    # angle5      [deg]   Real phase value of disc5 relative to disc1
    #                     (ignored if sim_chopper = 0)
    # angle6      [deg]   Real phase value of disc6 relative to disc1
    #                     (ignored if sim_chopper = 0)
    # n_per       []      Number of periods to simulate, useful to check for
    #                     frame overlap (ignored if sim_chopper = 0)
    # disc3_c     [mm]    Vertical position of the center of disc 3
    #                     (ignored if sim_chopper = 0)
    # disc4_c     [mm]    Vertical position of the center of disc 4
    #                     (ignored if sim_chopper = 0)
    # SC2_c       [mm]    Vertical position of the center of SC2 disc pair
    #                     (discs 5 and 6) (ignored if sim_chopper = 0)
    # b1_c        [mm]    Center b1 slit (Y-Coordinate)
    # b1_h        [mm]    Height of b1 slit
    # zb0_c       [mm]    Center of zb0 vertical slit (Y-Coordinate)
    # zb1_c       [mm]    Center of zb1 vertical slit (Y-Coordinate)
    # zb2_c       [mm]    Center of zb2 vertical slit (Y-Coordinate)
    # zb3_c       [mm]    Center of zb3 vertical slit (Y-Coordinate)
    # zb3_h       [mm]    Height of zb3 slit
    # bs1_c       [mm]    Center of bs1 vertical slit (Y-Coordinate)
    # bs1_h       [mm]    Height of bs1 slit
    # h3_c        [mm]    Center h3 slit (X-Coordinate)
    # h3_w        [mm]    Width of h3 slit
    # b3_c        [mm]    Center b3 slit (Y-Coordinate)
    # b3_h        [mm]    Height of b3 slit
    # gonio_theta [deg]   Value for gonio_theta (big_gonio).
    #                     The rotation axis is in the middle of NL2b, in case
    #                     gonio_z is zero
    # gonio_z     [mm]    Value for gonio_z. A null value means that the
    #                     vertical position of the axis of rotation of the
    #                     goniometer is in the center of NL2b
    # gonio_y     [mm]    Value for gonio_y. A null value means that the center
    #                     of sample is in the horizontal center of NL2b
    # top_gonio_z [mm]    Value for top_gonio_z. In the present simulation the
    #                     probe is installed on top_gonio and its surface is
    #                     aligned with respect to the beam center when its
    #                     value is 4.5 mm and gonio_z = 0
    # l_probe     [mm]    Length of the sample along the beam direction
    # w_probe     [mm]    Width of the sample perpendicular to beam direction
    # sample_file []      name of the file containing the reflectivities of the
    #                     sample to be simulated
    # backguard   [mm]    Value for the backguard. The backguard moves with big
    #                     gonio and is integral to it. When backguard is null,
    #                     its top edge is aligned with the center of NL2b
    # d_b3_probe  [mm]    Distance between the and the center of the probe
    # opt_nokX    []      Status of the optic element X (5a/5b/6/7/8/9): it may
    #                     be (0) for ng, (1) for vc and (2) for fc
    # nokX_r      [mm]    Absolute height (in lab-reference system) of the
    #                     optic element X (5a/5b/6/7/8/9) measured at the motor
    #                     located on reactor side, as provided by NICOS.
    #                     The height is relative to the vertical center of the
    #                     NL2b:
    #                     when nokX_r = nokX_s = 0, the center of the neutron
    #                     guide channel coincides with the center of NL2b
    # nokX_s      [mm]    Absolute height (in lab-reference system) of the
    #                     optic element X (5a/5b/6/7/8/9) measured at the motor
    #                     located on sample side, as provided by NICOS.
    #                     The height is relative to the vertical center of the
    #                     NL2b:
    #                     when nokX_r = nokX_s = 0, the center of the neutron
    #                     guide channel coincides with the center of NL2b
    # pivot_Pos   []      Position of pivot point (1-13)
    # yoke        [mm]    Height of scattering tube
    # det_table   [mm]    Horizontal distance of detector active surface from
    #                     pivot point

    opt_map = {
        'ng': 0,
        'vc': 1,
        'fc': 2,
    }

    def _prepare_params(self):
        params = []
        if self.gravity:
            params.append('-g')  # Switch gravitation on
        params.extend([
            # Diese Variable schaltet das Chopper-System ein (1) oder aus (0).
            # Lass sie bitte immer auf 1 eingestellt
            'sim_chopper=1',
            'rpm=%s' % self._dev(self._attached_rpm),
            'disc2_Pos=%s' % self._dev(self._attached_disc2_pos),
            'angle2=%s' % self._attached_chopper2.phase,
            'angle3=%s' % self._attached_chopper3.phase,
            'angle4=%s' % self._attached_chopper4.phase,
            'angle5=%s' % self._attached_chopper5.phase,
            'angle6=%s' % self._attached_chopper6.phase,

            # angle2 = chopper2.read(0)
            # angle3 = chopper3.read(0)
            # angle4 = chopper4.read(0)
            # angle5 = chopper5.read(0)
            # angle6 = chopper6.read(0)

            # Meas_Time ist die Messzeit, in Sekunden
            # 'n_per=%d' % (chopper_speed.read(0) * Meas_time / 60)

            'n_per=%d' % (self._attached_rpm.read(0) / 60 * self.preselection),
            'disc3_c=%s' % '0',  # self._dev(self._attached_chopper3),
            'disc4_c=%s' % '0',  # self._dev(self._attached_chopper3),

            'SC2_c=%s' % 0,  # self._dev(self._attached_sc2),  # 0

            'opt_nok3=%d' % ['ng', 'rc'].index(self._attached_nok3.mode),
            'opt_nok4=%d' % ['ng', 'rc'].index(self._attached_nok4.mode),

            'opt_nok5a=%d' % self.opt_map.get(self._attached_nok5a.mode, 0),
            'opt_nok5b=%d' % self.opt_map.get(self._attached_nok5b.mode, 0),
            'opt_nok6=%d' % self.opt_map.get(self._attached_nok6.mode, 0),
            'opt_nok7=%d' % self.opt_map.get(self._attached_nok7.mode, 0),
            'opt_nok8=%d' % self.opt_map.get(self._attached_nok8.mode, 0),
            'opt_nok9=%d' % self.opt_map.get(self._attached_nok9.mode, 0),

            'opt_b1=%d' % ['slit', 'gisans'].index(self._attached_b1.mode),
            'opt_b2=%d' % ['slit', 'gisans'].index(self._attached_b2.mode),
            'opt_zb0=%d' % ['slit', 'gisans'].index(self._attached_zb0.mode),
            'opt_zb1=%d' % ['slit', 'gisans'].index(self._attached_zb1.mode),
            'opt_zb2=%d' % ['slit', 'gisans'].index(self._attached_zb2.mode),
            'opt_zb3=%d' % ['slit', 'gisans'].index(self._attached_zb3.mode),
            'opt_bs1=%d' % ['slit', 'gisans'].index(self._attached_bs1.mode),

            'nok2_r=%s' % self._attached_nok2.read(0)[0],
            'nok2_s=%s' % self._attached_nok2.read(0)[1],
            'nok3_r=%s' % self._attached_nok3.read(0)[0],
            'nok3_s=%s' % self._attached_nok3.read(0)[1],
            'nok4_r=%s' % self._attached_nok4.read(0)[0],
            'nok4_s=%s' % self._attached_nok4.read(0)[1],
            'nok5a_r=%s' % self._attached_nok5a.read(0)[0],
            'nok5a_s=%s' % self._attached_nok5a.read(0)[1],
            'nok5b_r=%s' % self._attached_nok5b.read(0)[0],
            'nok5b_s=%s' % self._attached_nok5b.read(0)[1],
            'nok6_r=%s' % self._attached_nok6.read(0)[0],
            'nok6_s=%s' % self._attached_nok6.read(0)[1],
            'nok7_r=%s' % self._attached_nok7.read(0)[0],
            'nok7_s=%s' % self._attached_nok7.read(0)[1],
            'nok8_r=%s' % self._attached_nok8.read(0)[0],
            'nok8_s=%s' % self._attached_nok8.read(0)[1],
            'nok9_r=%s' % self._attached_nok9.read(0)[0],
            'nok9_s=%s' % self._attached_nok9.read(0)[1],

            'b1_c=%s' % self._dev(self._attached_b1.center),
            'b1_h=%s' % self._dev(self._attached_b1.opening),

            'zb0_c=%s' % self._dev(self._attached_zb0),
            'zb1_c=%s' % self._dev(self._attached_zb1),
            'zb2_c=%s' % self._dev(self._attached_zb2),
            'zb3_c=%s' % self._dev(self._attached_zb3.center),
            'zb3_h=%s' % self._dev(self._attached_zb3.opening),

            'bs1_c=%s' % self._dev(self._attached_bs1.center),
            'bs1_h=%s' % self._dev(self._attached_bs1.opening),

            'h3_c=%s' % self._dev(self._attached_h3.center),
            'h3_w=%s' % self._dev(self._attached_h3.opening),

            'b3_c=%s' % self._dev(self._attached_b3.center),
            'b3_h=%s' % self._dev(self._attached_b3.opening),

            'b2_c=%s' % self._dev(self._attached_b2.center),
            'b2_h=%s' % self._dev(self._attached_b2.opening),
            'h2_c=%s' % self._dev(self._attached_h2.center),
            'h2_w=%s' % self._dev(self._attached_h2.width),

            'gonio_theta=%s' % self._dev(self._attached_gonio_theta),
            'gonio_y=%s' % self._dev(self._attached_gonio_y),
            'gonio_z=%s' % self._dev(self._attached_gonio_z),
            'top_gonio_z=%s' % self._dev(self._attached_gonio_top_z,
                                         default='0'),

            'l_probe=%s' % self._attached_sample.length,
            'w_probe=%s' % self._attached_sample.width,
            'sample_name=%s' % self._attached_sample.samplename,
            'sample_file=%s' % os.path.join(self._attached_sample.datapath,
                                            self._attached_sample.sample_file),

            'backguard=%s' % self._dev(self._attached_backguard),

            'pivot_Pos=%s' % self._dev(self._attached_pivot, fmtstr='%d'),

            'yoke=%s' % self._dev(self._attached_yoke),

            'det_table=%s' % self._dev(self._attached_dettable),

            'd_b3_probe=%s' % self._dev(self._attached_d_b3_sample),
        ])
        return params
