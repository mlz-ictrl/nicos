description = 'Instrument modes not yet working'

group = 'optional'

devices = dict(
    instrument_mode = device('nicos.devices.generic.ManualSwitch',
        description = 'Modus of Measurement: GISANS or Reflectometry',
        states = ['GISANS', 'Reflectometry'],
        fmtstr = '%s',
    ),
)
