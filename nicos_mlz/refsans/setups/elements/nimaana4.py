description = 'Devices related to nimaana4 hardware'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
code_base = instrument_values['code_base']

tango_base = 'tango://nimaana4.refsans.frm2.tum.de:10000/test/ads/'

Vadd = 2.5

devices = dict(
    nimaana_air_temp = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'nima temperature SHT3x',
        device = 'nimaana4_ch2',
        poly = [-66.875, 218.75 / Vadd],
        unit = 'degC',
        pollinterval = 50,
    ),
    nimaana_air_rh = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'nima humidity SHT3x',
        device = 'nimaana4_ch1',
        poly = [-12.5, 125. / Vadd],
        unit = 'percent',
        pollinterval = 50,
    ),
)

for i in range(1, 5):
    devices[f'nimaana4_ch{i}'] = device('nicos.devices.entangle.Sensor',
        description = f'ADin{i - 1}',
        fmtstr = '%.4f',
        pollinterval = 0.5,
        precision = 0,
        comdelay = 0.1,
        comtries = 3,
        tangodevice = tango_base + f'ch{i}',
    )

for i in range(1, 3):
    devices[f'nimaana_resistor_{i}'] = device(code_base + 'analogencoder.Ohmmeter',
        description = f'Pool Resistor PT1000 {i}',
        device = f'nimaana4_ch{i + 2}',
        r_arb = 1000,
        u_high = Vadd,
        u_low = 0,
        unit = 'Ohm',
        pollinterval = None,
    )
    devices[f'nimaana_pool_{i}_temp'] = device(code_base + 'analogencoder.PTxxlinearC',
        description = f'Pool Temperature PT1000 {i}',
        device = f'nimaana_resistor_{i}',
        alpha = 0.003851,
        r0 = 1000,
        r_cable = 0.3,
        unit = 'degC',
        pollinterval = 50,
    )

devices[f'nimaana_pool_2_temp'].r_cable = 0.42
