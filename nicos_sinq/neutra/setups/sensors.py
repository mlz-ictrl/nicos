description = 'Beam line environmental sensors'

display_order = 95

pvprefix = 'SQ:NEUTRA:'

devices = dict(
    temperature = device('nicos.devices.epics.base.EpicsReadable',
        description = 'Beam line temperature',
        readpv = pvprefix + 'TEMP',
    ),
    humidity = device('nicos.devices.epics.base.EpicsReadable',
        description = 'Beam line relative humidity',
        readpv = pvprefix + 'RELHUM',
    ),
)
