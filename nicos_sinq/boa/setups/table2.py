description = 'BOA Table 2'

pvprefix = 'SQ:BOA:mcu2:'

devices = dict(
    t2tx = device('nicos.devices.epics.EpicsReadable',
        epicstimeout = 3.0,
        description = 'Table 2 x translation',
        readpv = pvprefix + 'T2TX',
    ),
    Table2 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 2',
        standard_devices = [
            't2tx',
        ]
    ),
)
