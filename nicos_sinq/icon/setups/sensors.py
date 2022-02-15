description = 'Beam line environmental sensors'

group = 'lowlevel'

display_order = 95

pvprefix = 'SQ:ICON:sensors:'

devices = dict(
    temperature = device('nicos.devices.epics.EpicsReadable',
        description = 'Beam line temperature',
        readpv = pvprefix + 'TEMP',
        unit = 'degC',
    ),
    humidity = device('nicos.devices.epics.EpicsReadable',
        description = 'Beam line relative humidity',
        readpv = pvprefix + 'RH',
        unit = '%',
    ),
)
