description = 'safety system and shutter'
includes = ['system']

devices = dict(
    saf      = device('nicos.toftof.safety.SafetyInputs',
                      i7053_1 = 'i7053_1',
                      i7053_2 = 'i7053_2',
                      i7053_3 = 'i7053_3'),
    i7053_1  = device('nicos.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70531'),
    i7053_2  = device('nicos.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70532'),
    i7053_3  = device('nicos.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70533'),

    shopen   = device('nicos.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/open',
                      lowlevel = True),
    shclose  = device('nicos.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/close',
                      lowlevel = True),
    shstatus = device('nicos.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/status',
                      lowlevel = True),
    shutter  = device('nicos.toftof.safety.Shutter',
                      open = 'shopen',
                      close = 'shclose',
                      status = 'shstatus',
                      unit = ''),
)
