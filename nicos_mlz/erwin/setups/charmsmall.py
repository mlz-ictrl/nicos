description = 'ErWIN detector devices'

group = 'optional'

tango_host = 'taco6.ictrl.frm2.tum.de'

tango_base = 'tango://%s:10000/test/scharm/' % tango_host

devices = dict(
    s_window = device('nicos.devices.entangle.PowerSupply',
        description = 'Window',
        tangodevice = tango_base + 'window',
        fmtstr = '%.1f',
        lowlevel = True,
        precision = 1,
    ),
    s_window_c = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Window current',
        device = 's_window',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        lowlevel = True,
    ),
    s_tripped = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Trip indicator',
        tangodevice = tango_base + 'trip',
        mapping = {
            '': 0,
            'High current seen': 1,
            'High current': 2,
            'Trip': 3,
        },
        pollinterval = 1,
    ),
    s_hv = device('nicos_mlz.erwin.devices.charmhv.HVSwitch',
        description = 'HV supply small detector',
        anodes = ['s_anode1', 's_anode2'],
        banodes = ['s_banode1'],
        cathodes = ['s_cathode1', 's_cathode2'],
        window = 's_window',
        trip = 's_tripped',
        pollinterval = 1,
        fmtstr = '%s',
        mapping = {
            'on': {
                's_anode1': 2175,
                's_anode2': 2200,
                's_banode1': 2185,
                's_cathode1': 200,
                's_cathode2': 200,
                's_window': -1500,
                'ramp': 50,
            },
            'off': {
                's_anode1': 0,
                's_anode2': 0,
                's_banode1': 0,
                's_cathode1': 0,
                's_cathode2': 0,
                's_window': 0,
                'ramp': 100,
            },
            'safe': {
                's_anode1': 200,
                's_anode2': 200,
                's_banode1': 200,
                's_cathode1': 200,
                's_cathode2': 200,
                's_window': -200,
                'ramp': 100,
            },
        },
    ),
)

for i in range(1, 3):
    devices['s_cathode%d' % i] = device('nicos.devices.entangle.PowerSupply',
        description = 'Cathode %d' % i,
        tangodevice = tango_base + 'cathode%d' % i,
        fmtstr = '%.1f',
        lowlevel = True,
        precision = 1,
    )
    devices['s_cathode%d_c' % i] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Cathode %d current' % i,
        device = 's_cathode%d' % i,
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        lowlevel = True,
    )

for i in range(1, 3):
    devices['s_anode%d' % i] = device('nicos.devices.entangle.PowerSupply',
        description = 'Anode %d HV' % i,
        tangodevice = tango_base + 'anode%d' % (i - 1),
        fmtstr = '%.1f',
        lowlevel = True,
        precision = 1,
    )
    devices['s_anode%s_c' % i] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Anode %d current' % i,
        device = 's_anode%d' % i,
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        lowlevel = True,
    )

for i in range(1, 2):
    devices['s_banode%d' % i] = device('nicos.devices.entangle.PowerSupply',
        description = 'Boundary anode %d HV' % i,
        tangodevice = tango_base + 'banode%d' % (i - 1),
        fmtstr = '%.1f',
        lowlevel = True,
        precision = 1,
    )
    devices['s_banode%s_c' % i] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Boundary anode %d current' % i,
        device = 'b_banode%d' % i,
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        lowlevel = True,
    )
