description = 'BOA Table 3'

pvprefix = 'SQ:BOA:turboPmac2:'

group = 'lowlevel'

devices = dict(
    t3tx = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Table 3 x translation',
        readpv = pvprefix + 'T3TX',
    ),
    Table3 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Table 3',
        standard_devices = [
            't3tx',
        ]
    ),
)
