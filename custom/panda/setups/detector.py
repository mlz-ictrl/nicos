#  -*- coding: utf-8 -*-

name='detectors'

group='internal'

includes=[]

modules=[]

devices = dict(

    timer    = device('nicos.generic.VirtualTimer',
                      lowlevel = True),

    mon1     = device('nicos.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 2500),

    mon2     = device('nicos.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 100),

    det1    = device('nicos.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000),

    det2    = device('nicos.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 200),

    det      = device('nicos.taco.FRMDetector',
                      t  = 'timer',
                      m1 = 'mon1',
                      m2 = 'mon2',
                      m3 = None,
                      z1 = 'det1',
                      z2 = 'det2',
                      z3 = None,
                      z4 = None,
                      z5 = None,
                      maxage = 3,
                      pollinterval = 0.5),
)

startupcode = ''
