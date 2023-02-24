description = 'Attenuator and PGFilter'

group = 'lowlevel'

devices = dict(
    fpg1 = device('nicos.devices.generic.ManualSwitch',
        description = 'First PG filter',
        states = ['out', 'in'],
    ),
    fpg2 = device('nicos.devices.generic.ManualSwitch',
        description = 'Second PG filter',
        states = ['out', 'in'],
    ),
)
