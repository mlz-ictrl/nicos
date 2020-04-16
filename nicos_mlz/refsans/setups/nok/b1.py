description = 'Slit B1 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
lprecision = 0.005
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index_r = 0
index_s = 1

devices = dict(
    b1 = device(code_base + 'slits.DoubleSlit',
        description = 'b1 end of Chopperburg',
        fmtstr = 'open: %.3f, zpos: %.3f',
        slit_r = 'b1r',
        slit_s = 'b1s',
        unit = 'mm',
    ),
    b1r = device(code_base + 'slits.SingleSlit',
        # length: 13.5 mm
        description = 'b1 slit, reactor side',
        motor = 'b1r_motor',
        masks = {
            'slit':   0.0,
            'point':  0.0,
            'gisans': 0.0,
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    b1s = device(code_base + 'slits.SingleSlit',
        # length: 13.5 mm
        description = 'xxx slit, sample side',
        motor = 'b1s_motor',
        masks = {
            'slit':   -0.0,
            'point':  -0.0,
            'gisans': -0.0,
        },
        nok_start = 2374.0,
        nok_end = 2387.5,
        nok_gap = 0,
        unit = 'mm',
        lowlevel = True,
    ),
    # b1r_axis = device('nicos.devices.generic.Axis',
    #     description = 'B1, reactorside',
    #     motor = 'b1r_motor',
    #     offset = 0.0,
    #     precision = lprecision,
    #     maxtries = 3,
    #     lowlevel = True,
    # ),
    # b1s_axis = device('nicos.devices.generic.Axis',
    #     description = 'B1, sampleside',
    #     motor = 'b1s_motor',
    #     offset = 0.0,
    #     precision = lprecision,
    #     maxtries = 3,
    #     lowlevel = True,
    # ),
    b1r_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M01), reactorside',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-133, 127), # XX: check values!
        ruler = 233.155, #abs enc! 60.0,
        lowlevel = True,
    ),
    # b1r_analog = device(code_base + 'beckhoff.nok.BeckhoffPoti',
    #     description = 'Poti for B1 Reactor no ref',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_r*10, # word adress
    #     slope = 10000,
    #     abslimits = (-1000, 1000),
    #     poly = [-301.3,0.01626],
    #     lowlevel = True or showcase_values['hide_poti'],
    # ),
    # b1r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
    #     description = 'calc error Motor and poti',
    #     motor = 'b1r_motor',
    #     analog = 'b1r_analog',
    #     lowlevel = True or showcase_values['hide_acc'],
    #     unit = 'mm'
    # ),
    b1s_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M0x',
        description = 'CAB1 controlled Blendenschild (M02), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10, # word adress
        slope = 10000,
        unit = 'mm',
        abslimits = (-102, 170),
        ruler = 140.388, #abs enc! -50.0,
        lowlevel = True,
    ),
    # b1s_analog = device(code_base + 'beckhoff.nok.BeckhoffPoti',
    #     description = 'Poti for B1 Sample no ref',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index_s*10, # word adress
    #     slope = 10000,
    #     abslimits = (-1000, 1000),
    #     poly = [-249.17,0.01626],
    #     lowlevel = True or showcase_values['hide_poti'],
    # ),
    # b1s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
    #     description = 'calc error Motor and poti',
    #     motor = 'b1s_motor',
    #     analog = 'b1s_analog',
    #     lowlevel = True or showcase_values['hide_acc'],
    #     unit = 'mm'
    # ),
)

alias_config = {
    'primary_aperture': {'b1.height': 300},
}
