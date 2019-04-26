description = 'NOK5a using Beckhoff controllers'

group = 'lowlevel'

showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')
tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/'

index_r = 2
index_s = 3

devices = dict(
    nok5a_r = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5a motor (M11), reactor side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word addresses
        slope = 10000,
        unit = 'mm',
        abslimits = (-70.0,67.68),
        ruler = 71.0889,
        lowlevel = True,
    ),
    nok5a_s_temp = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffTemp',
        description = 'Temperatur for nok5a_s Motor',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word address
        abslimits = (-1000, 1000),
        lowlevel = showcase_values['hide_temp'],
    ),
    nok5a_r_temp = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffTemp',
        description = 'Temperatur for nok5a_r Motor',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_r*10, # word address
        abslimits = (-1000, 1000),
        lowlevel = showcase_values['hide_temp'],
    ),
    nok5a_s = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M1x',
        description = 'nok5a motor (M12), sample side',
        tangodevice = tango_base + 'optic/io/modbus',
        address = 0x3020+index_s*10, # word addresses
        slope = 10000,
        unit = 'mm',
        abslimits = (-79.0,77.85),
        ruler = 79.6439,
        lowlevel = True,
    ),
    nok5a_r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK5a, reactor side',
        motor = 'nok5a_r',
        offset = 0.0,
        backlash = 0,
        precision = 0.02,
        maxtries = 3,
        unit = 'mm',
        lowlevel = True,
    ),
    nok5a_s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK5a, sample side',
        motor = 'nok5a_s',
        offset = 0.0,
        backlash = 0,
        precision = 0.02,
        maxtries = 3,
        unit = 'mm',
        lowlevel = True,
    ),
    nok5a = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        description = 'NOK5a',
        fmtstr = '%.2f, %.2f',
        nok_start = 2418.50,
        nok_length = 1719.20,
        nok_end = 4137.70,
        nok_gap = 1.0,
        nok_motor = [3108.00, 3888.00],
        offsets = (0.0, 0.0),
        inclinationlimits = (-100, 100),
        motor_r = 'nok5a_r_axis',
        motor_s = 'nok5a_s_axis',
        backlash = -2,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
            # 'pola': showcase_values['pola'],
        },
    ),
    nok5a_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'nok5a mode',
        device = 'nok5a',
        parameter = 'mode',
    ),
)
