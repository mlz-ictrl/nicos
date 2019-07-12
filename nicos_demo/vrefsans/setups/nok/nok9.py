description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok9 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 840.0 mm
        description = 'NOK9',
        nok_start = 9773.5,
        fmtstr = '%.2f, %.2f',
        nok_end = 10613.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok9r_axis',
        motor_s = 'nok9s_axis',
        nok_motor = [10023.5, 10362.7],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['ng'],
            'vc': global_values['vc'],
            'fc': global_values['fc'],
        }
    ),
    nok9r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-112.03425, 142.95925),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
    nok9s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, sample side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-114.51425, 142.62775),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
