description = 'A scale to weigh things'

pvprefix = 'SQ:ICON:scale:'

devices = dict(
    scale_weight = device('nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = 'Scale weight',
        readpv = pvprefix + 'WEIGHT_RBV',
        pva = False
    ),
)
