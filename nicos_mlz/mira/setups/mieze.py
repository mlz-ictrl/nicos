description = 'MIEZE measurement setup'
group = 'optional'

includes = ['cascade', 'guidehall', 'nl6', 'cbox1', 'cbox2',
            # 'guidefield',
            'rte1104', 'tuning']
excludes = ['guidefield']

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = dict(
    hsf1 = device('nicos.devices.entangle.PowerSupply',
        description = 'first coupling coil - Helmholtz coil',
        # tangodevice = tango_base + 'tti1/out1',
        tangodevice = tango_base + 'gf1/current',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    sf1 = device('nicos.devices.entangle.PowerSupply',
        description = 'first coupling coil - pi/2 flipper',
        # tangodevice = tango_base + 'tti1/out2',
        tangodevice = tango_base + 'gf2/current',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    hsf2 = device('nicos.devices.entangle.PowerSupply',
        description = 'second coupling coil - Helmholtz coil',
        # tangodevice = tango_base + 'tti2/out1',
        tangodevice = tango_base + 'gf3/current',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    sf2 = device('nicos.devices.entangle.PowerSupply',
        description = 'second coupling coil - pi/2 flipper',
        # tangodevice = tango_base + 'tti2/out2',
        tangodevice = tango_base + 'gf4/current',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
)
