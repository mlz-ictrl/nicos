description = 'Tensile machine'

group = 'optional'

devices = dict(
    teload = device('nicos.devices.generic.VirtualMotor',
        description = 'load value of the tensile machine',
        abslimits = (-50000, 50000),
        unit = 'N',
        fmtstr = '%.2f',
    ),
    # tepos = device('nicos.devices.generic.VirtualMotor',
    #     description = 'position value of the tensile machine',
    #     abslimits = (0, 70),
    #     # SPODI limits
    #     # abslimits = (-10, 55),
    #     unit = 'mm',
    #     fmtstr = '%.3f',
    # ),
    # teext = device('nicos.devices.generic.VirtualMotor',
    #     description = 'extension value of the tensile machine',
    #     abslimits = (-3000, 3000),
    #     unit = 'um',
    #     fmtstr = '%.3f',
    # ),
)

display_order = 40
