description = 'Capillary Optics'

group = 'lowlevel'
excludes = ['capillary']

devices = dict(
    # x-axis
    stcx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation x-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    stcx = device('nicos.devices.generic.Axis',
        description = 'Capillary translation x-Axis motor',
        motor = 'stcx_m',
        precision = 0.001,
    ),
    # y-axis
    stcy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation y-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    stcy = device('nicos.devices.generic.Axis',
        description = 'Capillary translation y-Axis motor',
        motor = 'stcy_m',
        precision = 0.001,
    ),
    # z-axis
    stcz_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation y-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    stcz = device('nicos.devices.generic.Axis',
        description = 'Capillary translation z-Axis motor',
        motor = 'stcz_m',
        precision = 0.001,
    ),
    # tip
    sgcx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary Tip motor',
        abslimits = (-2, 2),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    sgcx = device('nicos.devices.generic.Axis',
        description = 'Capillary Tip motor',
        motor = 'sgcx_m',
        precision = 0.001,
    ),
    # tilt
    sgcy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary Tilt motor',
        abslimits = (-2, 2),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    sgcy = device('nicos.devices.generic.Axis',
        description = 'Capillary Tilt motor',
        motor = 'sgcy_m',
        precision = 0.001,
    ),
)

startupcode = '''
SetDetectors(det_eiger)
'''
