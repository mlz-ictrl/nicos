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
        visibility = (),
    ),
    s_hv = device('nicos_mlz.erwin.devices.HVSwitch',
        description = 'HV supply small detector',
        anodes = ['s_anode1', 's_anode2'],
        banodes = ['s_banode1'],
        edges = ['s_edge1', 's_edge2'],
        window = 's_window',
        pollinterval = 1,
        fmtstr = '%s',
        mapping = {
            'on': {
                's_anode1': 2050,
                's_anode2': 2050,
                's_banode1': 2050,
                's_edge1': 100,
                's_edge2': 100,
                's_window': -1000,
                'ramp': 50,
            },
            'off': {
                's_anode1': 0,
                's_anode2': 0,
                's_banode1': 0,
                's_edge1': 0,
                's_edge2': 0,
                's_window': 0,
                'ramp': 100,
            },
            'safe': {
                's_anode1': 500,
                's_anode2': 500,
                's_banode1': 500,
                's_edge1': 100,
                's_edge2': 100,
                's_window': -1000,
                'ramp': 100,
            },
        },
        rampsteps = [
            (500, 2),
            (1000, 2),
            (1500, 2),
            (1750, 2),
            (1950, 2),
            ],
    ),
    s_hv_offtime = device('nicos_mlz.erwin.devices.charmhv.HVOffDuration',
        description = 'Duration of small detector below operating voltage',
        hv_supply = 's_hv',
        maxage = 120,
        pollinterval = 15,
    ),
    s_trip = device('nicos_mlz.erwin.devices.charmhv.HVTrip',
        hv_supply = 's_hv',
        maxage = 120,
        pollinterval = 15,
        visibility = (),
    ),
)

for i in (1, 2):
    devices[f's_edge{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Edge cathode {i}',
        tangodevice = tango_base + f'cathode{i}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
    )
    devices[f's_edge{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Edge cathode {i} current',
        device = f's_edge{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
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
        visibility = (),
    )
