description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

index = 4

devices = dict(
    zb0_motor = device(code_base + 'beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb0 (M13), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index*10, # word address
        slope = 10000,
        unit = 'mm',
        ruler = 302.679, #abs enc! -28.2111,
        abslimits = (-155.7889, 28.111099999999997),
        lowlevel = True,
    ),
    # zb0_a = device('nicos.devices.generic.Axis',
    #     description = 'zb0 axis',
    #     motor = 'zb0_motor',
    #     precision = 0.02,
    #     maxtries = 3,
    #     lowlevel = True,
    # ),
    zb0 = device(code_base + 'slits.SingleSlit',
        # length: 13 mm
        description = 'zb0, singleslit',
        motor = 'zb0_motor',
        nok_start = 4121.5,
        nok_end = 4134.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110 * optic_values['gisans_scale'],
        },
        unit = 'mm',
    ),
    # zb0_temp = device(code_base + 'beckhoff.nok.BeckhoffTemp',
    #     description = 'Temperatur for ZB0 Motor',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     lowlevel = showcase_values['hide_temp'],
    # ),
    # zb0_analog = device(code_base + 'beckhoff.nok.BeckhoffPoti',
    #     description = 'Poti for ZB0 no ref',
    #     tangodevice = tango_base + 'optic/io/modbus',
    #     address = 0x3020+index*10, # word address
    #     abslimits = (-1000, 1000),
    #     poly = [-176.49512271969755, 0.00794154091586989],
    #     lowlevel = True or showcase_values['hide_poti'],
    # ),
    # zb0_acc = device(code_base + 'nok_support.MotorEncoderDifference',
    #      description = 'calc error Motor and poti',
    #      motor = 'zb0_motor',
    #      analog = 'zb0_analog',
    #      lowlevel = True or showcase_values['hide_acc'],
    #      unit = 'mm'
    # ),
)
