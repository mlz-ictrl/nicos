description = 'POLI detector and counter card'
group = 'lowlevel'

includes = []
excludes = ['zeadetector']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    timer = device('nicos.devices.tango.TimerChannel',
                   tangodevice = tango_base + 'frmctr/timer',
                   fmtstr = '%.2f',
                   lowlevel = True,
                  ),
    mon1  = device('nicos.devices.tango.CounterChannel',
                   tangodevice = tango_base + 'frmctr/ctr1',
                   type = 'monitor',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),
    mon2  = device('nicos.devices.tango.CounterChannel',
                   tangodevice = tango_base + 'frmctr/ctr2',
                   type = 'monitor',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),
    ctr1  = device('nicos.devices.tango.CounterChannel',
                   tangodevice = tango_base + 'frmctr/ctr0',
                   type = 'counter',
                   fmtstr = '%d',
                   lowlevel = True,
                  ),

    det   = device('nicos.devices.generic.Detector',
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
