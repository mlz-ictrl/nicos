description = 'NOK5a using Beckhoff controllers'

group = 'lowlevel'

includes = ['zz_absoluts']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index_r = 2
index_s = 3

devices = dict(
    # nok5as_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for nok5a_s Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_s*10, # word address
    #     abslimits = (-1000, 1000),
    #     lowlevel = showcase_values['hide_temp'],
    #     unit = 'degC',
    # ),
    # nok5ar_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for nok5a_r Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_r*10, # word address
    #     abslimits = (-1000, 1000),
    #     lowlevel = showcase_values['hide_temp'],
    #     unit = 'degC',
    # ),
    # nok5ar_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5a, reactor side',
    #     motor = 'nok5ar',
    #     offset = 0.0,
    #     backlash = 0,
    #     precision = 0.02,
    #     maxtries = 3,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    # nok5as_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5a, sample side',
    #     motor = 'nok5as',
    #     offset = 0.0,
    #     backlash = 0,
    #     precision = 0.02,
    #     maxtries = 3,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    nok5a = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 1719.20 mm
        description = 'NOK5a',
        fmtstr = '%.2f, %.2f',
        nok_start = 2418.50,
        nok_end = 4137.70,
        nok_gap = 1.0,
        nok_motor = [3108.00, 3888.00],
        offsets = (0.0, 0.0),
        inclinationlimits = (-9.99, 9.99),
        motor_r = 'nok5ar_motor',
        motor_s = 'nok5as_motor',
        backlash = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
            # 'pola': showcase_values['pola'],
        },
    ),
)
