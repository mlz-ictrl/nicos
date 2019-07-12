description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok8 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 880.0 mm
        description = 'NOK8',
        fmtstr = '%.2f, %.2f',
        nok_start = 8870.5,
        nok_end = 9750.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok8r_axis',
        motor_s = 'nok8s_axis',
        nok_motor = [9120.0, 9500.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['ng'],
            'vc': global_values['vc'],
            'fc': global_values['fc'],
        },
    ),
    nok8r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-102.835, 128.415),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
    nok8s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-104.6, 131.65),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
