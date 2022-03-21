description = 'Morpheus test devices'

devices = dict(
    pfc = device('nicos.devices.generic.VirtualMotor',
        description = 'Polarizer magnet',
        abslimits = (-2.5, 2.5),
        unit = 'A',
    ),
    pff = device('nicos.devices.generic.VirtualMotor',
        description = 'Polarizer magnet',
        abslimits = (-2.5, 2.5),
        unit = 'A',
    ),
    ispin = device('nicos_sinq.morpheus.devices.ispin_morpheus.MorpheusSpin',
        magnet_c = 'pfc',
        magnet_f = 'pff',
        su_c = -1.2,
        su_f = -0.7,
    ),
)
