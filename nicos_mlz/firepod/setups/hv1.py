description = 'Detector 1 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det1/'

devices = dict(
    det1_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 1',
        tangodevice = tango_base + 'anode',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det1_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 1',
        device = 'det1_anode',
        parameter = 'current',
    ),
    det1_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 1',
        tangodevice = tango_base + 'drift',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det1_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 1',
        device = 'det1_drift',
        parameter = 'current',
    ),
)
