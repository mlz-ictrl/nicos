description = 'POLI detector and counter card'
group = 'lowlevel'

includes = []
excludes = ['zeadetector']

nethost = 'phys.poli.frm2'

devices = dict(
    timer = device('devices.taco.FRMTimerChannel',
                   tacodevice = '//%s/poli/frmctr/at' % nethost,
                   fmtstr = '%.2f',
                   lowlevel = True,
                  ),
    mon1  = device('devices.taco.FRMCounterChannel',
                   tacodevice = '//%s/poli/frmctr/a2' % nethost,
                   type = 'monitor',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),
    mon2  = device('devices.taco.FRMCounterChannel',
                   tacodevice = '//%s/poli/frmctr/a3' % nethost,
                   type = 'monitor',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),
    ctr1  = device('devices.taco.FRMCounterChannel',
                   tacodevice = '//%s/poli/frmctr/a1' % nethost,
                   type = 'counter',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),

    det   = device('devices.generic.Detector',
                   description = 'FRM II multichannel counter card',
                   timers = ['timer'],
                   monitors = ['mon1', 'mon2'],
                   counters = ['ctr1'],
                   maxage = 2,
                   pollinterval = 1.0,
                  ),
)

startupcode = '''
SetDetectors(det)
'''
