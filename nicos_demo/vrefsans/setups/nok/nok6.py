description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok6 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 1720.0 mm
        description = 'NOK6',
        fmtstr = '%.2f, %.2f',
        nok_start = 5887.5,
        nok_end = 7607.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok6r_axis',
        motor_s = 'nok6s_axis',
        nok_motor = [6137.0, 7357.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['ng'],
            'vc': global_values['vc'],
            'fc': global_values['fc'],
        },
    ),
    nok6r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-66.2, 96.59125),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
    nok6s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-81.0, 110.875),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
