description = 'virtual detector'
group = 'optional'

includes = ['system']

devices = dict(
    timer    = device('devices.generic.VirtualTimer',
                      lowlevel = True,
                     ),

    mon1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 1000,
                     ),

    ctr1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000,
                     ),

    ctr2     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 120,
                     ),

    det      = device('devices.taco.FRMDetector',
                      timer = 'timer',
                      monitors = ['mon1'],
                      counters = ['ctr1', 'ctr2'],
                      maxage = 3,
                      pollinterval = 0.5,
                     ),
)
