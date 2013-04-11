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

    ctr1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 5,
                     ),

    ctr2     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 1,
                     ),

    det      = device('devices.generic.MultiChannelDetector',
                      timer = 'timer',
                      monitors = ['mon1'],
                      counters = ['ctr1', 'ctr2'],
                      maxage = 3,
                      pollinterval = 0.5,
                     ),
)
