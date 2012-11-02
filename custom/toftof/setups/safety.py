description = 'safety system and shutter'
includes = ['system']

devices = dict(
    saf      = device('toftof.safety.SafetyInputs',
                      i7053_1 = 'i7053_1',
                      i7053_2 = 'i7053_2',
                      i7053_3 = 'i7053_3'),
    i7053_1  = device('devices.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70531'),
    i7053_2  = device('devices.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70532'),
    i7053_3  = device('devices.taco.DigitalInput',
                      lowlevel = True,
                      tacodevice = 'toftof/sec/70533'),

    shopen   = device('devices.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/open',
                      lowlevel = True),
    shclose  = device('devices.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/close',
                      lowlevel = True),
    shstatus = device('devices.taco.io.DigitalOutput',
                      tacodevice = '//toftofsrv/toftof/shutter/status',
                      lowlevel = True),
    shutter  = device('toftof.safety.Shutter',
                      open = 'shopen',
                      close = 'shclose',
                      status = 'shstatus',
                      unit = ''),
)
