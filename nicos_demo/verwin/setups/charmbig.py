description = 'Big ErWIN detector devices'

group = 'optional'

devices = dict(
    b_cathode1 = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = [0, 2225],
        unit = 'V',
        speed = 50,
        fmtstr = '%.1f',
    ),
    b_cathode2 = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = [0, 2225],
        unit = 'V',
        speed = 50,
        fmtstr = '%.1f',
    ),
    b_window = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = [-2225, 0],
        unit = 'V',
        speed = 50,
        fmtstr = '%.1f',
    ),
    b_tripped = device('nicos.devices.generic.ManualSwitch',
        description = 'Trip indicator',
        states = ['', 'High current seen', 'High current', 'Trip'],
        pollinterval = 1,
    ),
    b_hv = device('nicos_mlz.erwin.devices.charmhv.HVSwitch',
        description = 'HV supply small detector',
        anodes = ['b_anode%d' % i for i in range(1, 10)],
        banodes = ['b_banode%d' % i for i in range(1, 9)],
        cathodes = ['b_cathode1', 'b_cathode2'],
        window = 'b_window',
        trip = 'b_tripped',
        mapping = {
            'on': {
                'b_anode1': 2190,
                'b_anode2': 2192,
                'b_anode3': 2194,
                'b_anode4': 2197,
                'b_anode5': 2200,
                'b_anode6': 2203,
                'b_anode7': 2206,
                'b_anode8': 2208,
                'b_anode9': 2210,
                'b_banode1': 2192,
                'b_banode2': 2194,
                'b_banode3': 2196,
                'b_banode4': 2199,
                'b_banode5': 2199,
                'b_banode6': 2198,
                'b_banode7': 2197,
                'b_banode8': 2196,
                'b_cathode1': 200,
                'b_cathode2': 200,
                'b_window': -1500,
                'ramp': 5,
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
                'b_cathode1': 0,
                'b_cathode2': 0,
                'b_window': 0,
                'ramp': 10,
            },
            'safe': {
                'b_anode1': 200,
                'b_anode2': 200,
                'b_anode3': 200,
                'b_anode4': 200,
                'b_anode5': 200,
                'b_anode6': 200,
                'b_anode7': 200,
                'b_anode8': 200,
                'b_anode9': 200,
                'b_banode1': 200,
                'b_banode2': 200,
                'b_banode3': 200,
                'b_banode4': 200,
                'b_banode5': 200,
                'b_banode6': 200,
                'b_banode7': 200,
                'b_banode8': 200,
                'b_cathode1': 200,
                'b_cathode2': 200,
                'b_window': 200,
                'ramp': 10,
            },
        },
    ),
)

for i in range(1, 10):
    devices['b_anode%d' % i] = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = [0, 2225],
        unit = 'V',
        speed = 5,
        fmtstr = '%.1f',
    )

for i in range(1, 9):
    devices['b_banode%d' % i] = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = [0, 2225],
        unit = 'V',
        speed = 5,
        fmtstr = '%.1f',
    )