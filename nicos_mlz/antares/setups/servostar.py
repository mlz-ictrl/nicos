description = 'Large sample manipulation stage using servostar controller'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares'

devices = dict(
    stx_servostar = device('nicos.devices.entangle.Motor',
        description = 'Sample Translation X',
        tangodevice = tango_base + '/mani/x',
        pollinterval = 5,
        maxage = 12,
        precision = 0.01,
        userlimits = (0, 1010),
        abslimits = (0, 1010),
    ),
    sty_servostar = device('nicos.devices.entangle.Motor',
        description = 'Sample Translation Y',
        tangodevice = tango_base + '/mani/y',
        pollinterval = 5,
        precision = 0.01,
        maxage = 12,
        userlimits = (0, 580),
        abslimits = (0, 580),
    ),
    sry_servostar = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation around Y',
        tangodevice = tango_base + '/mani/phi',
        pollinterval = 5,
        maxage = 12,
        precision = 0.01,
        abslimits = (-9999, 9999),
        userlimits = (-9999, 9999),
    ),
)
