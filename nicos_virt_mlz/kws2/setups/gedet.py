# Setup for the GE detector
description = 'large GE He-3 detector'
group = 'lowlevel'
display_order = 24

eps = configdata('config_gedet.EIGHT_PACKS')
hv_values = configdata('config_gedet.HV_VALUES')

devices = dict(
    gedet_HV = device('nicos.devices.generic.ManualSwitch',
        description = 'switches the GE detector HV',
        states = ['off', 'on'],
    ),
    gedet_power = device('nicos.devices.generic.ManualSwitch',
        description = 'switches the GE detector 54V power supply',
        states = ['off', 'on'],
    ),
)

extended = dict(
    representative = 'gedet_HV',
)
