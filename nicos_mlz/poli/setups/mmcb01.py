description = 'Motorbox setup'

group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    axis1 = device('nicos.devices.generic.Axis',
        description = 'Axis 1',
        motor = device('nicos.devices.tango.Motor',
            tangodevice = tango_base + 'plc/plc_motor1',
            unit = 'deg',
        ),
        coder = None,
        precision = 0.05,
        abslimits = (0, 213.),
        userlimits = (0, 213.),
    ),
    axis2 = device('nicos.devices.generic.Axis',
        description = 'Axis 2',
        motor = device('nicos.devices.tango.Motor',
            tangodevice = tango_base + 'plc/plc_motor2',
            unit = 'deg',
        ),
        coder = device('nicos.devices.tango.Sensor',
            tangodevice = tango_base + 'plc/plc_coder2',
            unit = 'deg',
        ),
        precision = 0.05,
        abslimits = (-360., 360.),
        userlimits = (-360., 360.),
    ),
)
