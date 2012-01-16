description = 'reactor status devices'

devices = dict(
    Power    = device('nicos.taco.AnalogInput',
                      description = 'FRM II reactor power',
                      tacodevice = '//tacodb/frm2/reactor/power',
                      tacotimeout = 0.5,
                      pollinterval = 30,
                      maxage = 3600,
                      fmtstr = '%.1f',
                      unit = 'MW'),

    Crane    = device('nicos.taco.AnalogInput',
                      tacodevice = '//tacodb/frm2/smc10/pos',
                      tacotimeout = 0.5,
                      pollinterval = 5,
                      maxage = 30,
                      unit = 'm'),

    NL6      = device('nicos.taco.NamedDigitalInput',
                      description = 'NL6 shutter status',
                      mapping = {0: 'closed', 1: 'open'},
                      pollinterval = 30,
                      maxage = 60,
                      tacodevice = '//tacodb/frm2/shutter/nl6'),

    Sixfold  = device('nicos.taco.NamedDigitalInput',
                      description = 'Sixfold shutter status',
                      mapping = {0: 'closed', 1: 'open'},
                      pollinterval = 30,
                      maxage = 60,
                      tacodevice = '//tacodb/frm2/shutter/sixfold'),
)
