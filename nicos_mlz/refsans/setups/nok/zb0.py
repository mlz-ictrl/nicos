description = 'Slit ZB0 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')

tango_base = instrument_values['tango_base']

index = 4

devices = dict(
    zb0_m = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M13',
        description = 'CAB1 controlled zb0 (M13), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index*10, # word address
        slope = 10000,
        unit = 'mm',
        ruler = -28.2111,
        abslimits = (-155.7889, 28.111099999999997),
        lowlevel = True,
    ),
    zb0_a = device('nicos.devices.generic.Axis',
        description = 'zb0 axis',
        motor = 'zb0_m',
        precision = 0.02,
        maxtries = 3,
        lowlevel = True,
    ),
    zb0 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        # length: 13 mm
        description = 'zb0, singleslit',
        motor = 'zb0_a',
        nok_start = 4138.8,  # 4121.5
        nok_end = 4151.8,  # 4134.5
        # motor = 4145.35,  # 4128.5
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
    ),
    zb0_temp = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffTemp',
        description = 'Temperatur for ZB0 Motor',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index*10, # word address
        abslimits = (-1000, 1000),
        lowlevel = showcase_values['hide_temp'],
    ),
    zb0_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffPoti',
        description = 'Poti for ZB0 no ref',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index*10, # word address
        abslimits = (-1000, 1000),
        poly = [-176.49512271969755, 0.00794154091586989],
        lowlevel = True or showcase_values['hide_poti'],
    ),
    zb0_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb0_m',
         analog = 'zb0_obs',
         lowlevel = True or showcase_values['hide_acc'],
         unit = 'mm'
    ),
)
