description = 'config file for setup properties of devices for T-Spec machine'

group = 'configdata'

tango_base = 'tango://server.tspec.pnpi:10000/'

DP_CONF = {
    'description': 'Perpendicular detector position',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'cm',
    'abslimits': (-100, 100),
    'lowlevel': False,
}

CP_CONF = {
    'description': 'longitudinal  chopper position',
    'precision': 0.01,
    'speed': 0.5,
    'unit': 'cm',
    'abslimits': (-100, 100),
    'lowlevel': False,
}
