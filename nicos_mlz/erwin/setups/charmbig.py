description = 'ErwiN detector devices'

group = 'optional'

tango_host = 'erwinhw.erwin.frm2.tum.de'

tango_base = f'tango://{tango_host}:10000/erwin/bcharm/'


# erwin/bcharm/window
devices = dict(
    b_window = device('nicos.devices.entangle.PowerSupply',
        description = 'Window HV',
        tangodevice = tango_base + 'window',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
        warnlimits = (-1050, -950),
    ),
    b_window_c = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Window current',
        device = 'b_window',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        visibility = (),
    ),
    b_hv = device('nicos_mlz.erwin.devices.HVSwitch',
        description = 'HV supply big detector',
        anodes = [f'b_anode{i}' for i in range(1, 10)],
        banodes = [f'b_banode{i}' for i in range(1, 9)],
        edges = ['b_edge1', 'b_edge2'],
        window = 'b_window',
        fmtstr = '%s',
        mapping = {
            'on': {
                'b_anode1': 2050,
                'b_anode2': 2050,
                'b_anode3': 2050,
                'b_anode4': 2050,
                'b_anode5': 2050,
                'b_anode6': 2050,
                'b_anode7': 2050,
                'b_anode8': 2050,
                'b_anode9': 2050,
                'b_banode1': 2050,
                'b_banode2': 2050,
                'b_banode3': 2050,
                'b_banode4': 2050,
                'b_banode5': 2050,
                'b_banode6': 2050,
                'b_banode7': 2050,
                'b_banode8': 2050,
                'b_edge1': 100,
                'b_edge2': 100,
                'b_window': -1000,
                'ramp': 1.5 * 60,
            },
            'off': {
                'b_anode1': 0,
                'b_anode2': 0,
                'b_anode3': 0,
                'b_anode4': 0,
                'b_anode5': 0,
                'b_anode6': 0,
                'b_anode7': 0,
                'b_anode8': 0,
                'b_anode9': 0,
                'b_banode1': 0,
                'b_banode2': 0,
                'b_banode3': 0,
                'b_banode4': 0,
                'b_banode5': 0,
                'b_banode6': 0,
                'b_banode7': 0,
                'b_banode8': 0,
                'b_edge1': 0,
                'b_edge2': 0,
                'b_window': 0,
                'ramp': 6 * 60,
            },
            'safe': {
                'b_anode1': 500,
                'b_anode2': 500,
                'b_anode3': 500,
                'b_anode4': 500,
                'b_anode5': 500,
                'b_anode6': 500,
                'b_anode7': 500,
                'b_anode8': 500,
                'b_anode9': 500,
                'b_banode1': 500,
                'b_banode2': 500,
                'b_banode3': 500,
                'b_banode4': 500,
                'b_banode5': 500,
                'b_banode6': 500,
                'b_banode7': 500,
                'b_banode8': 500,
                'b_edge1': 100,
                'b_edge2': 100,
                'b_window': -1000,
                'ramp': 6 * 60,
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
    b_hv_offtime = device('nicos_mlz.erwin.devices.charmhv.HVOffDuration',
        description = 'Duration of big detector below operating voltage',
        hv_supply = 'b_hv',
        maxage = 120,
        pollinterval = 15,
    ),
    b_trip = device('nicos_mlz.erwin.devices.charmhv.HVTrip',
        hv_supply = 'b_hv',
        maxage = 120,
        pollinterval = 15,
        visibility = (),
    ),
)

# erwin/bcharm/cathode1
# erwin/bcharm/cathode2
for i in range(1, 3):
    devices[f'b_edge{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Edge cathode {i}',
        tangodevice = tango_base + f'cathode{i}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
        warnlimits = (95, 105),
    )
    devices[f'b_edge{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Edge cathode {i} current',
        device = f'b_edge{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        visibility = (),
    )

# erwin/bcharm/anode0
# erwin/bcharm/anode1
# erwin/bcharm/anode2
# erwin/bcharm/anode3
# erwin/bcharm/anode4
# erwin/bcharm/anode5
# erwin/bcharm/anode6
# erwin/bcharm/anode7
# erwin/bcharm/anode8
for i in range(1, 10):
    devices[f'b_anode{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Anode {i} HV',
        tangodevice = tango_base + f'anode{i - 1}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
        warnlimits = (1950, 2050),
    )
    devices[f'b_anode{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Anode {i} current',
        device = f'b_anode{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        visibility = (),
    )

# erwin/bcharm/banode0
# erwin/bcharm/banode1
# erwin/bcharm/banode2
# erwin/bcharm/banode3
# erwin/bcharm/banode4
# erwin/bcharm/banode5
# erwin/bcharm/banode6
# erwin/bcharm/banode7
# not in use erwin/bcharm/banode8
for i in range(1, 9):
    devices[f'b_banode{i}'] = device('nicos.devices.entangle.PowerSupply',
        description = f'Boundary anode {i} HV',
        tangodevice = tango_base + f'banode{i - 1}',
        fmtstr = '%.1f',
        visibility = (),
        precision = 1,
        warnlimits = (1950, 2050),
    )
    devices[f'b_banode{i}_c'] = device('nicos.devices.generic.ReadonlyParamDevice',
        description = f'Boundary anode {i} current',
        device = f'b_banode{i}',
        parameter = 'current',
        copy_status = True,
        fmtstr = '%.6g',
        visibility = (),
    )
