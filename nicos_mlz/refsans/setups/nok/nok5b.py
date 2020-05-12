description = 'NOK5b using Beckhoff controllers'

group = 'lowlevel'
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

excludes = ['nok5b_old']

index_r = 5
index_s = 6

devices = dict(
    nok5br = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5b motor (M21), reactor side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word addresses
        slope = 10000,
        unit = 'mm',
        abslimits = (-37.9997, 91.9003),
        ruler = 266.947, #abs enc! 38.0997,
        lowlevel = True,
    ),
    # nok5br_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for nok5b_r Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_r*10, # word address
    #     abslimits = (-1000, 1000),
    #     lowlevel = showcase_values['hide_temp'],
    # ),
    # nok5bs_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for nok5b_s Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_s*10, # word address
    #     abslimits = (-1000, 1000),
    #     lowlevel = showcase_values['hide_temp'],
    # ),
    nok5bs = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5b motor (M22), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10, # word addresses
        slope = 10000,
        unit = 'mm',
        abslimits = (-53.7985, 76.1015),
        ruler = 300.101, #abs enc! 53.8985,
        lowlevel = True,
    ),
    # nok5br_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5b, reactor side',
    #     motor = 'nok5b_r',
    #     offset = 0.0,
    #     backlash = 0,
    #     precision = 0.02,
    #     maxtries = 3,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    # nok5bs_axis = device('nicos.devices.generic.Axis',
    #     description = 'Axis of NOK5b, sample side',
    #     motor = 'nok5b_s',
    #     offset = 0.0,
    #     backlash = 0,
    #     precision = 0.02,
    #     maxtries = 3,
    #     unit = 'mm',
    #     lowlevel = True,
    # ),
    nok5b = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 1719.20 mm
        description = 'NOK5b',
        fmtstr = '%.2f, %.2f',
        nok_start = 4153.50,
        nok_end = 5872.70,
        nok_gap = 1.0,
        offsets = (0.0, 0.0),
        inclinationlimits = (-14.99, 14.99),
        motor_r = 'nok5br',
        motor_s = 'nok5bs',
        nok_motor = [4403.00, 5623.00],
        backlash = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        },
    ),
)
