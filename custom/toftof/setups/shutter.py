description = 'shutter'
includes = ['system']

devices = dict(
    shopen = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/open',
                   lowlevel = False,
                   ),
    shclose = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/close',
                   lowlevel = False,
                   ),
    shstatus = device('nicos.taco.io.DigitalOutput',
                   tacodevice = '//toftofsrv/toftof/shutter/status',
                   lowlevel = False,
                   ),
    shutter    = device('nicos.toftof.shutter.Shutter',
                   open = 'shopen',
                   close = 'shclose',
                   status = 'shstatus',
                   unit = '', 
                   ),
)
