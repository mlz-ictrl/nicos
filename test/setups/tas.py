#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

name = 'TAS setup'

modules = ['nicos.commands.tas']

includes = ['stdsystem']

sysconfig = dict(
    instrument = 'Tas',
)

devices = dict(
    Sample = device('devices.tas.TASSample'),
    t_phi = device('devices.generic.VirtualMotor',
        abslimits = (-120, 120),
        curvalue = 0,
        speed = 0,
        jitter = 0.01,
        precision = 0.02,
        unit = 'deg',
    ),
    t_psi = device('devices.generic.VirtualMotor',
        abslimits = (0, 360),
        curvalue = 0,
        speed = 0,
        jitter = 0.01,
        precision = 0.02,
        unit = 'deg',
    ),
    t_mfh = device('test.utils.TestDevice',
        unit = 'deg',
        abslimits = (0, 360),
    ),
    t_mfv = device('test.utils.TestDevice',
        unit = 'deg',
        abslimits = (0, 360),
    ),
    t_mono = device('devices.tas.Monochromator',
        unit = 'A-1',
        theta = 't_mth',
        twotheta = 't_mtt',
        focush = 't_mfh',
        focusv = 't_mfv',
        focmode = 'horizontal',
        abslimits = (0.1, 10),
        dvalue = 3.325,
        crystalside = 1,
    ),
    t_mth = device('devices.generic.VirtualMotor',
        curvalue = 10,
        unit = 'deg',
        abslimits = (-180, 180),
        jitter = 0.02,
        precision = 0.05,
    ),
    t_mtt = device('devices.generic.VirtualMotor',
        curvalue = 20,
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
    t_ana = device('devices.tas.Monochromator',
        unit = 'A-1',
        theta = 't_ath',
        twotheta = 't_att',
        focush = None,
        focusv = None,
        reltheta = True,
        abslimits = (0.1, 10),
        dvalue = 3.325,
        crystalside = 1,
    ),
    t_ath = device('devices.generic.VirtualMotor',
        curvalue = 10,
        unit = 'deg',
        abslimits = (-180, 270),
        jitter = 0.02,
        precision = 0.05,
    ),
    t_att = device('devices.generic.VirtualMotor',
        curvalue = -20,
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
    t_ki = device('devices.tas.Wavevector',
        unit = 'A-1',
        base = 't_mono',
        tas = 'Tas',
        scanmode = 'CKI',
    ),
    t_kf = device('devices.tas.Wavevector',
        unit = 'A-1',
        base = 't_ana',
        tas = 'Tas',
        scanmode = 'CKF',
    ),
    t_alpha = device('devices.generic.VirtualMotor',
        curvalue = 0,
        unit = 'deg',
        abslimits = (-360, 360),
    ),
    Tas = device('devices.tas.TAS',
        cell = 'Sample',
        mono = 't_mono',
        phi = 't_phi',
        psi = 't_psi',
        ana = 't_ana',
        alpha = 't_alpha',
        instrument = 'Tas',
        countloopdelay = 0.002,
        collimation = '20 20 20 60',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
    ),
    vtasdet = device('devices.tas.virtual.VirtualTasDetector',
        tas = 'Tas',
    ),
    sgx = device('devices.generic.VirtualMotor',
        description = 'X axis sample gonio',
        abslimits = (-5, 5),
        unit = 'deg',
    ),
    sgy = device('devices.generic.VirtualMotor',
        description = 'Y axis sample gonio',
        abslimits = (-5, 5),
        unit = 'deg',
    ),
    vg1 = device('devices.tas.VirtualGonio',
        description = 'Gonio along orient1 reflex',
        cell = 'Sample',
        gx = 'sgx',
        gy = 'sgy',
        axis = 1,
        unit = 'deg',
    ),
    vg2 = device('devices.tas.VirtualGonio',
        description = 'Gonio along orient2 reflex',
        cell = 'Sample',
        gx = 'sgx',
        gy = 'sgy',
        axis = 2,
        unit = 'deg',
    ),
)
