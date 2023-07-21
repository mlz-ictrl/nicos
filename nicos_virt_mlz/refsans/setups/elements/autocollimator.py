description = 'autocollimator, water subtracted, vendor Trioptic'

group = 'lowlevel'

devices = dict(
    # autocollimator = device(code_base + 'TriangleMaster',
    #     description = description,
    #     tangodevice = tango_host,
    #     visibility = (),
    #     unit = '',
    # ),
    autocollimator_theta = device('nicos.devices.generic.VirtualMotor',
        description = description + ', autocollimator Y on PC',
        abslimits = (0, 10),
        unit = 'deg',
    ),
    autocollimator_phi = device('nicos.devices.generic.VirtualMotor',
        description = description + ', autocollimator X on PC',
        abslimits = (0, 10),
        unit = 'deg',
    ),
)
