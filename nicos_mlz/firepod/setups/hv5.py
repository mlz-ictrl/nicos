description = 'Detector 5 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det5/'

devices = dict(
    det5_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 5',
        tangodevice = tango_base + 'anode',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det5_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 5',
        device = 'det5_anode',
        parameter = 'current',
    ),
    det5_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 5',
        tangodevice = tango_base + 'drift',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det5_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 5',
        device = 'det5_drift',
        parameter = 'current',
    ),
)
