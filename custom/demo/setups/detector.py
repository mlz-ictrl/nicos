description = 'virtual detector'
group = 'lowlevel'

includes = ['system']
excludes = ['refsans', 'sans', 'qmchannel', 'pgaa', 'vtof', 'vspodi']

devices = dict(
    timer    = device('devices.generic.VirtualTimer',
                      lowlevel = True,
                     ),

    mon1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 1000,
                      fmtstr = '%d',
                     ),

    ctr1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000,
                      fmtstr = '%d',
                     ),

    ctr2     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 120,
                      fmtstr = '%d',
                     ),

    det      = device('devices.generic.Detector',
                      description = 'Classical detector with single channels',
                      timers = ['timer'],
                      monitors = ['mon1'],
                      counters = ['ctr1', 'ctr2'],
                      maxage = 3,
                      pollinterval = 0.5,
                     ),
)

startupcode = '''
SetDetectors(det)
'''
