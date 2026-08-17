description = 'Detector 2 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det2/'

devices = dict(
    det2_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 2',
        tangodevice = tango_base + 'anode',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det2_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 2',
        device = 'det2_anode',
        parameter = 'current',
    ),
    det2_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 2',
        tangodevice = tango_base + 'drift',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det2_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 2',
        device = 'det2_drift',
        parameter = 'current',
    ),
)
