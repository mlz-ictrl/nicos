description = 'Devices for the emagnet SANS sample holder'

excludes = ['sample']

devices = dict(
    mz = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Table Height',
        precision = 0.01,
        unit = 'mm',
        abslimits = (0, 1),
    ),
    mom = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample table Rotation',
        precision = 0.01,
        unit = 'deg',
        abslimits = (-360, 360),
    ),
)
