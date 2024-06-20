description = 'Devices related to nimaana4 hardware'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
code_base = instrument_values['code_base']

ana4gpio = 'pt1000x4x01'
tango_base = f'tango://{ana4gpio}.refsans.frm2.tum.de:10000/test/ads/'
visibility = {}
Vadd = 2.5

devices = {}

for i in range(1, 5):
    devices[f'{ana4gpio}_ch{i}'] = device('nicos.devices.entangle.Sensor',
        description = f'ADin{i - 1}',
        fmtstr = '%.4f',
        pollinterval = 0.5,
        precision = 0,
        comdelay = 0.1,
        comtries = 3,
        tangodevice = tango_base + f'ch{i}',
        visibility = visibility,
    )
    devices[f'{ana4gpio}_resistor_{i}'] = device(code_base + 'analogencoder.Ohmmeter',
        description = f'Pool Resistor PT1000 {i}',
        device = f'{ana4gpio}_ch{i}',
        r_arb = 1000,
        u_high = Vadd,
        u_low = 0,
        unit = 'Ohm',
        pollinterval = None,
        visibility = visibility,
    )
    devices[f'{ana4gpio}_{i}_temp'] = device(code_base + 'analogencoder.PTxxlinearC',
        description = f'Pool Temperature PT1000 {i}',
        device = f'{ana4gpio}_resistor_{i}',
        alpha = 0.003851,
        r0 = 1000,
        r_cable = 0.0,
        unit = 'degC',
        pollinterval = 50,
    )
