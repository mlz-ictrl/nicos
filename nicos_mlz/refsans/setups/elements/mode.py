description = 'Instrument modes'

group = 'lowlevel'

devices = dict(
    mode = device('nicos.devices.generic.ManualSwitch',
        description = 'Modus of Measurement: GISANS or Reflectometry',
        states = ['GISANS', 'Reflectometry'],
        fmtstr = '%s',
    ),
)
