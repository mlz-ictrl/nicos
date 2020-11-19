description = 'Camera focusing at position 2 - micro setup'

group = 'lowlevel'

display_order = 45

pvprefix = 'SQ:ICON:usetup:'

devices = dict(
    focus_micro = device('nicos.devices.epics.EpicsWindowTimeoutDevice',
        epicstimeout = 3.0,
        description = 'Camera focus micro setup',
        writepv = pvprefix + 'SETP',
        readpv = pvprefix + 'POS',
        precision = 10,
        window = 5,
        timeout = 20,
        unit = 'um',
        abslimits = (-1000, 6000),
    ),
)
