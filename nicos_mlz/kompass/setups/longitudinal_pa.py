description = 'Kompass setup for longitudinal polarisation analysis mode'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2.tum.de:10000/kompass/'

excludes = ['lpa_kompass', 'lpa_panda']

devices = dict(
    coil_1 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for horizontal field 1 at sample',
        tangodevice = tango_base + 'kepco/current5',
        abslimits = (-20, 20),
        orientation = (0.53, 0.53, 0),    # mT - calibrated 30/04/2021 at KOMPASS
        calibrationcurrent = 10,          # A
    ),
    coil_1_voltage = device('nicos.devices.entangle.Sensor',
        description = 'horizontal field 1 voltage monitoring',
        tangodevice = tango_base + 'kepco/voltage5',
    ),
    coil_2 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for horizontal field 2 at sample',
        tangodevice = tango_base + 'kepco/current6',
        abslimits = (-20, 20),
        orientation = (0.53, -0.53, 0),    # mT - calibrated 30/04/2021 at KOMPASS
        calibrationcurrent = 10,           # A
    ),
    coil_2_voltage = device('nicos.devices.entangle.Sensor',
        description = 'horizontal field 2 voltage monitoring',
        tangodevice = tango_base + 'kepco/voltage6',
    ),
    coil_3 = device('nicos_mlz.panda.devices.guidefield.VectorCoil',
        description = 'Powersupply for vertical field at sample',
        tangodevice = tango_base + 'kepco/current7',
        abslimits = (-20, 20),
        orientation = (0, 0, 2.33),     # mT - calibrated 30/04/2021 at KOMPASS
        calibrationcurrent = 2,         # A  only 2A at KOMPASS, at PANDA was 10 A
    ),
    coil_3_voltage = device('nicos.devices.entangle.Sensor',
        description = 'vertical field voltage monitoring',
        tangodevice = tango_base + 'kepco/voltage7',
    ),
    gf = device('nicos_mlz.panda.devices.guidefield.GuideField',
        description = 'Vector field at sample location',
        alpha = 'alphastorage',
        coils = ['coil_1', 'coil_2', 'coil_3'],
        alphaoffset = 0,
        field = 0.8,    # mT   at KOMPASS, at PANDA was 1 mT
        mapping = {'off': None,
                   'par':   ( 1., 0., 0.),
                   '-par':  (-1., 0., 0.),
                   'perp':  ( 0., 1., 0.),
                   '-perp': ( 0.,-1., 0.),
                   'z':     ( 0., 0., 1.),
                   '-z':    ( 0., 0.,-1.),
                   'up':    ( 0., 0., 1.),
                   'down':  ( 0., 0.,-1.),
                   '0':     ( 0., 0., 0.)},
    ),
    sf1 = device('nicos.devices.polarized.KFlipper',
        description = 'Spin Flipper 1 (before sample)',
        flip = 'kepco2_current', # 'sf1_f',
        corr = 'kepco1_current', # 'sf1_c',
        kvalue = 'ki',
        flipcurrent = [-0.18037, -0.43804],
        compcurrent = 2.35,
    ),
    sf2 = device('nicos.devices.polarized.KFlipper',
        description = 'Spin Flipper 2 (after sample)',
        flip = 'kepco4_current', # 'sf2_f',
        corr = 'kepco3_current', # 'sf2_c',
        kvalue = 'ki',  # for inelastic LPA should be changed back to "kf"
        # for kf=1.55+befilter
        flipcurrent = [0.083, 0.38],
        compcurrent = 1.45,
        # for kf=1.94 +/-pg
        # flipcurrent = [0.765, 0],
        # compcurrent = 2.4474,
    ),
)

for i in range(8):
    devices[f'kepco{i}_current'] = device('nicos.devices.entangle.PowerSupply',
        description = f'kepco power supply {i}',
        tangodevice = tango_base + f'kepco/current{i}',
        fmtstr = '%.3f',
    )
    devices[f'kepco{i}_voltage'] = device('nicos.devices.entangle.Sensor',
        description = f'kepco power supply {i} voltage monitoring',
        tangodevice = tango_base + f'kepco/voltage{i}',
    )
