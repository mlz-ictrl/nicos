description = 'Detector 3 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det3/'

devices = dict(
    det3_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 3',
        tangodevice = tango_base + 'anode',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
        visibility = {'namespace', 'metadata'},
    ),
    det3_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 3',
        device = 'det3_anode',
        parameter = 'current',
        fmtstr = '%.1e',
        visibility = {'namespace', 'metadata'},
    ),
    det3_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 3',
        tangodevice = tango_base + 'drift',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
        visibility = {'namespace', 'metadata'},
    ),
    det3_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 3',
        device = 'det3_drift',
        parameter = 'current',
        fmtstr = '%.1e',
        visibility = {'namespace', 'metadata'},
    ),
    det3_hv = device('nicos_mlz.firepod.devices.detectorhv.DetectorHVChannelSwitch',
        description = 'HV switch of detector 3',
        drift = 'det3_drift',
        anode = 'det3_anode',
        visibility = {'namespace', 'metadata'},
    ),
)
