#  -*- coding: utf-8 -*-

description = 'single detector'

group = 'internal'

devices = dict(
    timer    = device('nicos.taco.FRMTimerChannel',
                      tacodevice = 'puma/frmctr/at',
                      lowlevel = True),

    mon1     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a1',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    mon2     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a2',
                      type = 'monitor',
                      lowlevel = True,
                      ),

    det1     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a3',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det2     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/a4',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det3     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b1',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det4     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b2',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det5     = device('nicos.taco.FRMCounterChannel',
                      tacodevice = 'puma/frmctr/b3',
                      type = 'counter',
                      lowlevel = True,
                      ),

    det      = device('nicos.taco.FRMDetector',
                      timer  = 'timer',
                      monitors = ['mon1', 'mon2'],
                      counters = ['det1', 'det2', 'det3', 'det4', 'det5'],
                      maxage = 1,
                      pollinterval = 1),
)

startupcode = ''
