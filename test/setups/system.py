#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

name = 'test system setup'

sysconfig = dict(
    cache = 'localhost:14877',
    experiment = 'Exp',
    instrument = 'Tas',
    datasinks = ['testsink'],
)

modules = ['nicos.commands.tas']


devices = dict(
    sample   = device('nicos.tas.TASSample'),

    testsink = device('test.utils.TestSink'),

    Exp      = device('nicos.experiment.Experiment',
                      sample = 'sample',
                      loglevel = 'info',
                      dataroot = '../root/data',
                      scriptdir = '.',
                      elog = False,
                      lowlevel = False),

    t_phi    = device('nicos.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      initval = 0,
                      speed = 1,
                      jitter = 0.01,
                      unit = 'deg'),

    t_psi    = device('nicos.generic.VirtualMotor',
                      abslimits = (0, 360),
                      initval = 0,
                      speed = 2,
                      jitter = 0.05,
                      unit = 'deg'),

    t_mono   = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 't_mth',
                      twotheta = 't_mtt',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                      dvalue = 3.325),

    t_mth    = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      jitter = 0.02),

    t_mtt    = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180)),

    t_ana    = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 't_ath',
                      twotheta = 't_att',
                      focush = None,
                      focusv = None,
                      reltheta = True,
                      abslimits = (0, 10),
                      dvalue = 3.325),

    t_ath    = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      jitter = 0.02),

    t_att    = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180)),

    Tas      = device('nicos.tas.TAS',
                      cell = 'sample',
                      mono = 't_mono',
                      phi = 't_phi',
                      psi = 't_psi',
                      ana = 't_ana',
                      instrument = 'Tas'),
)
