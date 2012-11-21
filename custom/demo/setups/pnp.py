group = 'optional'

devices = dict(
    B  = device('devices.generic.VirtualMotor',
                abslimits = (0, 10),
                unit = 'T'),
)
