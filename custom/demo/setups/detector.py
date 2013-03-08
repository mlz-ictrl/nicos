description = 'virtual detector'
group = 'lowlevel'

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

    # use the showcase TAS counter that simulates Bragg peaks and phonons
    ctr1     = device('devices.generic.virtual.VirtualTasCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 5,
                      tas = 'tas',
                     ),

    ctr2     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 1,
                     ),

    det      = device('devices.taco.FRMDetector',
                      timer = 'timer',
                      monitors = ['mon1'],
                      counters = ['ctr1', 'ctr2'],
                      maxage = 3,
                      pollinterval = 0.5,
                     ),
)
