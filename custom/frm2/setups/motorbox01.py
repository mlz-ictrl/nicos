description = 'Motorbox setup'

group = 'plugplay'

nethost = setupname

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    axis1 = device('devices.generic.Axis',
        description = 'Axis 1',
        motor = device('devices.tango.Motor',
            tangodevice = tango_base + 'phytron0/y_mot',
            unit = 'deg',
        ),
        coder = device('devices.tango.Sensor',
            tangodevice = tango_base + 'phytron0/y_enc',
            unit = 'deg',
        ),
        precision = 0.05,
        abslimits = (-360., 360.),
    ),
)
