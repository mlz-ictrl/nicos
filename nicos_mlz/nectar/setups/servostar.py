description = 'Sample manipulation stage using servostar controller'
group = 'optional'

tango_base = 'tango://nectarhw.nectar.frm2.tum.de:10000/nectar'

devices = dict(
    stx = device('nicos.devices.tango.Motor',
        description = 'Sample Translation X',
        tangodevice = tango_base + '/mani/x',
        pollinterval = 5,
        maxage = 12,
        userlimits = (0, 1010),
        abslimits = (0, 1010),
        comtries = 5,
    ),
    sty = device('nicos.devices.tango.Motor',
        description = 'Sample Translation Y',
        tangodevice = tango_base + '/mani/y',
        pollinterval = 5,
        maxage = 12,
        userlimits = (0, 580),
        abslimits = (0, 580),
        comtries = 5,
    ),
    sry = device('nicos.devices.tango.Motor',
        description = 'Sample Rotation around Y',
        tangodevice = tango_base + '/mani/phi',
        pollinterval = 5,
        maxage = 12,
        userlimits = (0, 360),
        abslimits = (0, 360),
        comtries = 5,
    ),
)
