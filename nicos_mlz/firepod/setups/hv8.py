description = 'Detector 8 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det8/'

devices = dict(
    det8_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 8',
        tangodevice = tango_base + 'anode',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det8_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 8',
        device = 'det8_anode',
        parameter = 'current',
    ),
    det8_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 8',
        tangodevice = tango_base + 'drift',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det8_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 8',
        device = 'det8_drift',
        parameter = 'current',
    ),
)
