description = 'Plug connector switch for neodry60E'

#group = 'lowlevel'

devices = dict(
    valve_switch = device('nicos.devices.generic.ManualSwitch',
        description = 'plug connector switch for neodry60E',
        states = ('on', 'off'),
    ),
)
