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
                      timer  = 'timer',
                      monitors = ['mon1', 'mon2'],
                      counters = ['det1', 'det2'],
                      #~ counters = ['det2'],
                      maxage = 1,
                      pollinterval = 0.5),
)

startupcode = ''
