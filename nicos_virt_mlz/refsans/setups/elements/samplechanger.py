description = 'Sample table devices'

group = 'lowlevel'

devices = dict(
    samplechanger = device('nicos.devices.generic.Axis',
        description = 'Samplechanger. towards TOFTOF is plus',
        motor = 'samplechanger_motor',
        # coder = 'samplechanger_enc',
        precision = 0.01,
    ),
    samplechanger_motor = device('nicos.devices.generic.VirtualMotor',
        description = 'Samplechanger axis motor  100mm/3.5min 0,48mm/sec',
        visibility = (),
        unit = 'mm',
        abslimits = [-186, 150], #MP offset==0 2021-03-29 13:18:30 abslimits = [14,350],
    ),
    samplechanger_enc = device('nicos.devices.generic.VirtualCoder',
        description = 'Samplechanger axis coder',
        motor = 'samplechanger_motor',
        unit = 'mm',
        visibility = (),
    ),
)
