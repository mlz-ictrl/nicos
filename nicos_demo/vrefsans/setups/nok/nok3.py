description = "neutronguide, radialcollimator"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok3 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 600.0 mm
        description = 'NOK3',
        fmtstr = '%.2f, %.2f',
        nok_start = 680.0,
        nok_end = 1280.0,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok3r_axis',
        motor_s = 'nok3s_axis',
        nok_motor = [831.0, 1131.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['rc'],
            'vc': global_values['ng'],
            'fc': global_values['ng'],
        },
    ),
    nok3r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.967, 47.783),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        unit = 'mm',
        lowlevel = True,
    ),
    nok3s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-20.9435, 40.8065),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
