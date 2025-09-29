description = 'Capillary Optics'

group = 'lowlevel'
excludes = ['capillary']

devices = dict(
    # x-axis
    tcx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation x-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    tcx = device('nicos.devices.generic.Axis',
        description = 'Capillary translation x-Axis motor',
        motor = 'tcx_m',
        precision = 0.001,
    ),
    # y-axis
    tcy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation y-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    tcy = device('nicos.devices.generic.Axis',
        description = 'Capillary translation y-Axis motor',
        motor = 'tcy_m',
        precision = 0.001,
    ),
    # z-axis
    tcz_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary translation y-Axis motor',
        abslimits = (-7.5, 7.5),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    tcz = device('nicos.devices.generic.Axis',
        description = 'Capillary translation z-Axis motor',
        motor = 'tcz_m',
        precision = 0.001,
    ),
    # tip
    gcx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary Tip motor',
        abslimits = (-2, 2),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    gcx = device('nicos.devices.generic.Axis',
        description = 'Capillary Tip motor',
        motor = 'gcx_m',
        precision = 0.001,
    ),
    # tilt
    gcy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Capillary Tilt motor',
        abslimits = (-2, 2),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    gcy = device('nicos.devices.generic.Axis',
        description = 'Capillary Tilt motor',
        motor = 'gcy_m',
        precision = 0.001,
    ),
)

startupcode = '''
SetDetectors(det_eiger)
'''
