description = 'shutter'
includes = ['system']

devices = dict(
    shopen = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/open',
                   lowlevel = True),
    shclose = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/close',
                   lowlevel = True),
    shstatus = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/status',
                   lowlevel = True),
    shutter    = device('nicos.toftof.shutter.Shutter',
                   open = 'shopen',
                   close = 'shclose',
                   status = 'shstatus',
                   unit = ''),
)
