name = 'reactor status devices'

devices = dict(
    Power    = device('nicos.io.AnalogInput',
                      description = 'FRM II reactor power',
                      tacodevice = '//tacodb/frm2/reactor/power',
                      tacotimeout = 0.5,
                      pollinterval = 30,
                      maxage = 3600,
                      fmtstr = '%.1f',
                      unit = 'MW'),

    Crane    = device('nicos.io.AnalogInput',
                      tacodevice = '//tacodb/frm2/smc10/pos',
                      tacotimeout = 0.5,
                      pollinterval = 5,
                      maxage = 30,
                      unit = 'm'),

    NL6_in   = device('nicos.io.DigitalInput',
                      lowlevel = True,
                      tacodevice = '//tacodb/frm2/shutter/nl6'),

    NL6      = device('nicos.switcher.ReadonlySwitcher',
                      description = 'NL6 shutter status',
                      pollinterval = 30,
                      maxage = 60,
                      readable = 'NL6_in',
                      states = ['closed', 'open'],
                      values = [0, 1]),

    Sixf_in  = device('nicos.io.DigitalInput',
                      lowlevel = True,
                      tacodevice = '//tacodb/frm2/shutter/sixfold'),

    Sixfold  = device('nicos.switcher.ReadonlySwitcher',
                      description = 'Sixfold shutter status',
                      pollinterval = 30,
                      maxage = 60,
                      readable = 'Sixf_in',
                      states = ['closed', 'open'],
                      values = [0, 1]),
)
