#  -*- coding: utf-8 -*-

description='detectors'

group='internal'

includes=[]

modules=[]

devices = dict(


    timer    = device('nicos.taco.FRMTimerChannel',
                      tacodevice = 'panda/frmctr/at',
                      lowlevel = True),

    mon1     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a1',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    mon2     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a2',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    det1     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a3',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det2     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'panda/frmctr/a4',
                      type = 'counter',
                      lowlevel = True,
                      ),


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
