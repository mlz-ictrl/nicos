# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

name = 'test_puma setup'

includes = ['stdsystem']
monostates = ['GE311', 'PG002', 'CU220', 'CU111', 'None']
monodevices = ['mono_ge311', 'mono_pg002', 'mono_cu220', 'mono_cu111',
               'mono_dummy']
magazinepos = [(315.4, '8'), (45.46, '1'), (135.4, '2'), (225.4, '4')]

devices = dict(
    phi = device('nicos_mlz.puma.devices.CombAxis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-5, 116.1),
        ),
        obs = [],
        precision = 0.005,
        offset = 0.,
        maxtries = 5,
        loopdelay = 0.02,
        fix_ax = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-15., 355.),
        ),
        iscomb = False,
    ),
    af = device('nicos_mlz.puma.devices.FocusAxis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-55, 55),
            curvalue = 4.92,
        ),
        obs = [],
        uplimit = 5,
        lowlimit = -5,
        flatpos = 4.92,
        startpos = 4,
        precision = 0.25,
        maxtries = 15,
        loopdelay = 0.02,
    ),
    polyswitch = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
    ),
    mtt = device('nicos_mlz.puma.devices.MttAxis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-110.1, 0),
        ),
        io_flag = 'polyswitch',
        polyswitch = 'polyswitch',
        obs = [],
        precision = 0.011,
        offset = 0.0,
        maxtries = 1,
        backlash = -0.1,
        loopdelay = 0.02,
        polysleep = 0.02,
    ),
    ath = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (0, 60),
        precision = 0.05,
    ),
    cad = device('nicos_mlz.puma.devices.CoupledAxis',
        tt = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-117, 117),
            precision = 0.05,
        ),
        th = 'ath',
        fmtstr = '%.3f',
        unit = 'deg',
        precision = .1,
    ),
    rd6_cad = device('nicos_mlz.puma.devices.StackedAxis',
        bottom = 'cad',
        top = 'rd6',
    ),
    # Magazine
    mag = device('nicos.devices.generic.Axis',
        description = 'monochromator magazine moving axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (20, 340),
            curvalue = 315.4,
        ),
        precision = 0.05,
        offset = 0,
        maxtries = 10,
        dragerror = 90,
        loopdelay = 2,
    ),
    io_mag = device('nicos.devices.generic.ReadonlySwitcher',
        readable = 'mag',
        mapping = {
            1: 45.46,
            2: 135.4,
            4: 225.4,
            8: 315.4,
        },
        fallback = 0,
        unit = '',
        visibility = (),
    ),
    magazine = device('nicos_mlz.puma.devices.SenseSwitch',
        description = 'Monochromator magazine',
        moveables = ['mag'],
        readables = ['io_mag'],
        mapping = dict(zip(monostates[:4], magazinepos)),
        precision = [0.2, 0],
        unit = '',
        blockingmove = True,
        fallback = '<unknown>',
        timeout = 300,
    ),
    # Magnetic Lock
    mlock_op = device('nicos_mlz.puma.devices.VirtualLogoFeedback',
        input = 'mlock_set',
        visibility = (),
    ),
    mlock_cl = device('nicos_mlz.puma.devices.VirtualLogoFeedback',
        input = 'mlock_set',
        inverted = True,
        visibility = (),
    ),
    mlock_set = device('nicos_mlz.puma.devices.VirtualDigitalOutput',
        visibility = (),
    ),
    mlock = device('nicos_mlz.puma.devices.MagLock',
        description = 'Magnetic lock at magazine',
        states = monostates[:4],
        magazine = 'magazine',
        io_open = 'mlock_op',
        io_closed = 'mlock_cl',
        io_set = 'mlock_set',
        unit = '',
    ),
)
