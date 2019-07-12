description = "neutronguide, radialcollimator"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok4 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 1000.0 mm
        description = 'NOK4',
        fmtstr = '%.2f, %.2f',
        nok_start = 1326.0,
        nok_end = 2326.0,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok4r_axis',
        motor_s = 'nok4s_axis',
        nok_motor = [1477.0, 2177.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['rc'],
            'vc': global_values['ng'],
            'fc': global_values['ng'],
        },
    ),
    nok4r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK4, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-20.477, 48.523),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        unit = 'mm',
        lowlevel = True,
    ),
    nok4s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK4, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.3025, 41.1975),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
