description = 'manual devices for test bambus table'

group = 'lowlevel'

devices = dict(
    avtt     = device('nicos.devices.generic.ManualMove',
                      description = 'Analyzer vertical two-theta',
                      default = 20,
                      unit = 'deg',
                      fmtstr = '%.2f',
                      abslimits = (0, 180),
                     ),
    avgx     = device('nicos.devices.generic.ManualMove',
                      description = 'tilt of the analyzer crystals',
                      default = 0,
                      unit = 'deg',
                      fmtstr = '%.2f',
                      abslimits = (-20, 20),
                     ),
    avct     = device('nicos.devices.generic.ManualSwitch',
                      description = 'type of analyzer PG crystal',
                      states = ['PGCX04', 'PGCX07', 'PGCX07-R717', 'PGCX07-R552',],
                     ),
    avef     = device('nicos.devices.generic.ManualSwitch',
                      description = 'Ef of analyzer',
                      states = [3, 5],
                      unit = 'meV',
                      fmtstr = '%.1f',
                     ),
)
