description = 'Goniometer Motors'

group = 'lowlevel'

tango_base_motor = 'tango://bioxs:10000/motor/'

devices = dict(
    # Omega
    sth_m = device('nicos.devices.entangle.Motor',
        description = 'Omega Axis Motor',
        tangodevice = tango_base_motor + 'phymotion/sth_motor',
        visibility = (),
    ),
    sth = device('nicos.devices.generic.Axis',
        description = 'Omega Axis Motor',
        motor = 'sth_m',
        precision = 0.001,
    ),
    # 2 theta
    stt_m = device('nicos.devices.entangle.Motor',
        description = '2 Theta Axis Motor',
        tangodevice = tango_base_motor + 'phymotion/stt_motor',
        visibility = (),
    ),
    stt = device('nicos.devices.generic.Axis',
        description = '2 Theta Axis Motor',
        motor = 'stt_m',
        precision = 0.001,
    ),
)
