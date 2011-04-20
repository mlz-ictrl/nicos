#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id: devices.py 469 2011-04-17 17:30:06Z gbrandl $
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

name = 'devices for the setup'

#includes = []

devices = dict(

    # -- System devices -------------------------------------------------------

    System   = device('nicos.system.System',
                      datapath = 'data/',
                      cache = 'Cache',
                      datasinks = ['conssink', 'filesink'],
                      instrument = 'tas',
                      experiment = 'Exp',
                      notifiers = []),

    Exp      = device('nicos.experiment.Experiment',
                      sample = 'Sample'),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),

    Cache    = device('nicos.cache.client.CacheClient',
                      lowlevel = True,
                      server = 'localhost',
                      prefix = 'nicos/',
                      loglevel = 'info'),

    # -- TAS devices and axes -------------------------------------------------

    Sample   = device('nicos.tas.TASSample'),

    tas      = device('nicos.tas.TAS',
                      instrument='VTAS',
                      responsible='R. Esponsible <responsible@frm2.tum.de>',
                      detectors=['det'],
                      cell = 'Sample',
                      phi = 'phi',
                      psi = 'psi',
                      mono = 'mono',
                      ana = 'ana'),

    phi      = device('nicos.virtual.VirtualMotor',
                      abslimits = (-180, 180), 
                      initval = 0,
                      unit = 'deg'),

    psi      = device('nicos.virtual.VirtualMotor',
                      abslimits = (0, 360),
                      initval = 0,
                      unit = 'deg'),

    mono     = device('nicos.virtual.VirtualMotor',
                      unit = 'A-1',
                      abslimits = (0, 10),
                      initval = 2.662),

    ana      = device('nicos.virtual.VirtualMotor',
                      unit = 'A-1',
                      abslimits = (0, 10),
                      initval = 2.662),

    ki       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'tas',
                      opmode = 'CKI',
                      abslimits = (0, 10)),

    kf       = device('nicos.tas.Wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'tas',
                      opmode = 'CKF',
                      abslimits = (0, 10)),

    # -- miscellaneous axes ---------------------------------------------------

    m1       = device('nicos.virtual.VirtualMotor',
                      lowlevel = True,
                      #loglevel = 'debug',
                      initval = 1,
                      abslimits = (-100, 100),
                      speed = 0.5,
                      unit = 'deg'),

    m2       = device('nicos.virtual.VirtualMotor',
                      lowlevel = True,
                      loglevel = 'debug',
                      initval = 0.5,
                      abslimits = (-100, 100),
                      speed = 1,
                      unit = 'deg'),

#    sxl      = device('nicos.motor.Motor', tacodevice = 'mira/aper1/m1', abslimits= (-35, 65)),
#    sxr      = device('nicos.motor.Motor', tacodevice = 'mira/aper1/m2', abslimits= (-65, 35)),
#    sxb      = device('nicos.motor.Motor', tacodevice = 'mira/aper1/m3', abslimits= (-65, 35)),
#    sxt      = device('nicos.motor.Motor', tacodevice = 'mira/aper1/m4', abslimits= (-35, 65)),

    sxl      = device('nicos.virtual.VirtualMotor', abslimits = (-20, 40), unit = 'mm', initval = 0),
    sxr      = device('nicos.virtual.VirtualMotor', abslimits = (-40, 20), unit = 'mm', initval = 0),
    sxb      = device('nicos.virtual.VirtualMotor', abslimits = (-50, 30), unit = 'mm', initval = 0),
    sxt      = device('nicos.virtual.VirtualMotor', abslimits = (-30, 50), unit = 'mm', initval = 0),
    slit     = device('nicos.slit.Slit', left = 'sxl', right = 'sxr', bottom = 'sxb', top = 'sxt'),

    c1       = device('nicos.virtual.VirtualCoder',
                      lowlevel = True,
                      motor = 'm1',
                      unit = 'deg'),

    a1       = device('nicos.axis.Axis',
                      motor = 'm1',
                      coder = 'c1',
                      obs = ['c1'],
                      abslimits = (0, 100),
                      userlimits = (0, 50),
                      precision = 0,
                      pollinterval = 0.5),

    a2       = device('nicos.axis.Axis',
                      motor = 'm2',
                      coder = 'm2',
                      obs = [],
                      precision = 0,
                      abslimits = (0, 100)),

    sw       = device('nicos.switcher.Switcher',
                      moveable = 'a2',
                      states = ['in', 'out'],
                      values = [1, 0],
                      precision = 0),

    # Power = device('nicos.io.AnalogInput',
    #                description = 'FRM II reactor power',
    #                tacodevice = '//tacodb/frm2/reactor/power',
    #                tacolog = True,
    #                loglevel = 'debug',
    #                fmtstr = '%.1f',
    #                unit = 'MW'),

    # -- detector -------------------------------------------------------------

    timer    = device('nicos.virtual.VirtualTimer',
                      lowlevel = True),

    mon1     = device('nicos.virtual.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 1000),

    ctr1     = device('nicos.virtual.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000),

    det      = device('nicos.detector.FRMDetector',
                      t  = 'timer',
                      m1 = 'ctr1',
                      m2 = None,
                      m3 = None,
                      z1 = 'mon1',
                      z2 = None,
                      z3 = None,
                      z4 = None,
                      z5 = None,
                      maxage = 3,
                      pollinterval = 0.5),
)

startupcode = '''
print 'startup code executed'
'''
