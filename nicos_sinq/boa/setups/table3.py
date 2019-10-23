description = 'BOA Table 3'

pvprefix = 'SQ:BOA:mcu2:'

devices = dict(
    t3tx = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = 3.0,
        description = 'Table 3 x translation',
        readpv = pvprefix + 'T3TX',
    ),
    Table3 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 3',
        standard_devices = [
            't3tx',
        ]
    ),
)
