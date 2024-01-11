description = 'alias for the current sample changer'

group = 'lowlevel'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/sample/changer/'

devices = dict(
    # use an Actuator as referencing is broken on this hw
    sc_y = device('nicos.devices.entangle.Actuator',
        description = 'Sample Changer Axis motor',
        tangodevice = tango_base + 'sc',
        fmtstr = '%.2f',
        abslimits = (-0, 600),
    ),
    SampleChanger = device('nicos.devices.generic.DeviceAlias'),
)
