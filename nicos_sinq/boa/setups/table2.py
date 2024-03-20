description = 'BOA Table 2'

pvprefix = 'SQ:BOA:mcu2:'

devices = dict(
    t2tx = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Table 2 x translation',
        readpv = pvprefix + 'T2TX',
    ),
    Table2 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Table 2',
        standard_devices = [
            't2tx',
        ]
    ),
)
