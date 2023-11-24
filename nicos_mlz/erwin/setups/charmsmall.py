description = 'ErWIN detector devices'

group = 'optional'

tango_host = 'erwinhw.erwin.frm2.tum.de'

tango_base = f'tango://{tango_host}:10000/test/scharm/'

devices = dict(
    s_window = device('nicos.devices.entangle.PowerSupply',
        description = 'Window',
        tangodevice = tango_base + 'window',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
    ),
    s_window_c = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Window current',
        device = 's_window',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        visibility = (),
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
    s_hv = device('nicos_mlz.erwin.devices.HVSwitch',
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
    devices[f's_cathode{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Cathode {i}',
        tangodevice = tango_base + f'cathode{i}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
    )
    devices[f's_cathode{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Cathode {i} current',
        device = f's_cathode{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        visibility = (),
    )

for i in range(1, 3):
    devices[f's_anode{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Anode {i} HV',
        tangodevice = tango_base + f'anode{i - 1}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
    )
    devices[f's_anode{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Anode {i} current',
        device = f's_anode{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        visibility = (),
    )

for i in range(1, 2):
    devices[f's_banode{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Boundary anode {i} HV',
        tangodevice = tango_base + f'banode{i - 1}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
    )
    devices[f's_banode{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Boundary anode {i} current',
        device = f's_banode{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        unit = 'µA',
        visibility = (),
    )
