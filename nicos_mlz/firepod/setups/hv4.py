description = 'Detector 4 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det4/'

devices = dict(
    det4_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 4',
        tangodevice = tango_base + 'anode',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det4_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 4',
        device = 'det4_anode',
        parameter = 'current',
    ),
    det4_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 4',
        tangodevice = tango_base + 'drift',
        precision = 2,
        requires = {'level': 'admin'},
    ),
    det4_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 4',
        device = 'det4_drift',
        parameter = 'current',
    ),
)
