description = 'Detector 7 HV devices'

group = 'lowlevel'

tango_base = 'tango://firepodhw:10000/firepod/det7/'

devices = dict(
    det7_anode = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode HV of detector 7',
        tangodevice = tango_base + 'anode',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
    ),
    det7_anode_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode HV current of detector 7',
        device = 'det7_anode',
        parameter = 'current',
        fmtstr = '%.1e',
    ),
    det7_drift = device('nicos.devices.entangle.PowerSupply',
        description = 'Drift HV of detector 7',
        tangodevice = tango_base + 'drift',
        precision = 2,
        fmtstr = '%.0f',
        requires = {'level': 'admin'},
    ),
    det7_drift_current = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Drift HV current of detector 7',
        device = 'det7_drift',
        parameter = 'current',
        fmtstr = '%.1e',
    ),
    det7_hv = device('nicos_mlz.firepod.devices.detectorhv.DetectorHVChannelSwitch',
        description = 'HV switch of detector 7',
        drift = 'det7_drift',
        anode = 'det7_anode',
    ),
)
