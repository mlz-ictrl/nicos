description = "neutronguide, radialcollimator"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg01']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok4 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 1000.0 mm
        description = 'NOK4',
        fmtstr = '%.2f, %.2f',
        nok_start = 1326.0,
        nok_end = 2326.0,
        nok_gap = 1.0,
        inclinationlimits = (-40, 40),
        motor_r = 'nok4r_axis',
        motor_s = 'nok4s_axis',
        nok_motor = [1477.0, 2177.0],
        precision = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['rc'],
            'vc': optic_values['ng'],
            'fc': optic_values['ng'],
        },
    ),
    nok4r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK4, reactor side',
        motor = 'nok4r_motor',
        # obs = ['nok4r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok4r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok4r_motor',
         device2 = 'nok4r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok4s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK4, sample side',
        motor = 'nok4s_motor',
        # obs = ['nok4s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok4s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok4s_motor',
         device2 = 'nok4s_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
