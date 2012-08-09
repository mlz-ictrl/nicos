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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'test triple-axis setup'
group = 'basic'

includes = ['system']

modules = ['nicos.commands.tas']

sysconfig = dict(
    instrument = 'tas',
)

devices = dict(
    tas      = device('nicos.tas.TAS',
                      description = 'test triple-axis spectrometer',
                      instrument = 'VTAS',
                      responsible = 'R. Esponsible <responsible@frm2.tum.de>',
                      energytransferunit = 'meV',
                      axiscoupling = False,
                      cell = 'Sample',
                      phi = 'phi',
                      psi = 'psi',
                      mono = 'mono',
                      ana = 'ana',
                      alpha = None),

    phi      = device('nicos.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      initval = 0,
                      unit = 'deg'),

    alpha    = device('nicos.generic.VirtualMotor',
                      abslimits = (0, 50),
                      unit = 'deg'),

    psi      = device('nicos.generic.VirtualMotor',
                      abslimits = (0, 360),
                      initval = 0,
                      unit = 'deg'),

    mono     = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      dvalue = 2.88,
                      theta = 'mth',
                      twotheta = 'mtt',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10)),

    mth      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 45),

    mtt      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 90),

    ana      = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      dvalue = 3.325,
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10)),

    ath      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 35),

    att      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 70),

    ki       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'tas',
                      scanmode = 'CKI',
                      abslimits = (0, 10)),

    kf       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'tas',
                      scanmode = 'CKF',
                      abslimits = (0, 10)),

    ssl      = device('nicos.generic.VirtualMotor',
                      abslimits = (-20, 40),
                      lowlevel = True,
                      unit = 'mm'),
    ssr      = device('nicos.generic.VirtualMotor',
                      abslimits = (-40, 20),
                      lowlevel = True,
                      unit = 'mm'),
    ssb      = device('nicos.generic.VirtualMotor',
                      abslimits = (-50, 30),
                      lowlevel = True,
                      unit = 'mm'),
    sst      = device('nicos.generic.VirtualMotor',
                      abslimits = (-30, 50),
                      lowlevel = True,
                      unit = 'mm'),
    ss       = device('nicos.generic.Slit',
                      left = 'ssl',
                      right = 'ssr',
                      bottom = 'ssb',
                      top = 'sst',
                      opmode = 'offcentered'),
)
