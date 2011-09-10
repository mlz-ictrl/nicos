#  -*- coding: utf-8 -*-

name = 'devices for the setup'

includes = []

modules=[]

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
