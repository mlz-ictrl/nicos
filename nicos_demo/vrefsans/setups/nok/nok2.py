description = "neutronguide"

group = 'lowlevel'

global_values = configdata('global.GLOBAL_Values')

devices = dict(
    nok2 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        # length: 300.0 mm
        description = 'NOK2',
        fmtstr = '%.2f, %.2f',
        nok_start = 334.0,
        nok_end = 634.0,
        nok_gap = 1.0,
        inclinationlimits = (-11.34, 13.61),
        motor_r = 'nok2r_axis',
        motor_s = 'nok2s_axis',
        nok_motor = [408.5, 585.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': global_values['ng'],
            'rc': global_values['ng'],
            'vc': global_values['ng'],
            'fc': global_values['ng'],
        },
    ),
    nok2r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK2, reactor side',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-22.36, 10.88),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
    nok2s_axis = device('nicos.devices.generic.Axis',
         description = 'Axis of NOK2, sample side',
         motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-21.61, 6.885),
            unit = 'mm',
            speed = 1.,
        ),
        backlash = 0,
        precision = 0.5,
        lowlevel = True,
    ),
)
