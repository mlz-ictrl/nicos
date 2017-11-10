description = 'Slits before analyser'

group = 'optional'

includes = ['motorbus6']

devices = dict(
    st_dslit = device('nicos_mlz.puma.devices.ipc_puma.Motor',
        bus = 'motorbus6',
        addr = 67,
        slope = 4500,
        unit = 'mm',
        abslimits = (-5.5, 30),
        zerosteps = 500000,
        lowlevel = True,
    ),

    co_dslit = device('nicos_mlz.puma.devices.ipc_puma.Coder',
        bus = 'motorbus6',
        addr = 97,
        slope = 80,
        zerosteps = 159,
        unit = 'mm',
        lowlevel = True,
    ),
    dslit = device('nicos.devices.generic.Axis',
        description = 'Slit before detector',
        motor = 'st_dslit',
        coder = 'co_dslit',
        obs = [],
        precision = 0.05,
        offset = 0,
        maxtries = 10,
    ),
)
