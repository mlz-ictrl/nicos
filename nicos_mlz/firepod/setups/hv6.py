description = 'Detector 6 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det6/'

devices = dict(
    det6_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 6',
        tangodevice = tango_base + 'anode',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
    ),
    det6_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 6',
        device = 'det6_anode',
        parameter = 'current',
        fmtstr = '%g',
    ),
    det6_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 6',
        tangodevice = tango_base + 'drift',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
    ),
    det6_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 6',
        device = 'det6_drift',
        parameter = 'current',
        fmtstr = '%g',
    ),
)
