description = 'A scale to weigh things'

pvprefix = 'SQ:ICON:scale:'

devices = dict(
    scale_weight = device('nicos.devices.epics.EpicsReadable',
        description = 'Scale weight',
        readpv = pvprefix + 'WEIGHT_RBV',
        pva = False
    ),
)
