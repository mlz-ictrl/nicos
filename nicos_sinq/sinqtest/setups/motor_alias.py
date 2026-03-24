description = 'Alias to motors'

includes = ['alias_incl']

devices = dict(
    motor_1 = device('nicos.devices.generic.manual.ManualMove',
                     description = '1st test motor',
                     unit = 'rpm',
                     abslimits = (0, 2000),
                     ),
    motor_2 = device('nicos.devices.generic.manual.ManualMove',
                     description = '2nd test motor',
                     unit = 'rpm',
                     abslimits = (0, 2000),
                     ),
    motor_alias = device('nicos.core.device.DeviceAlias',
        alias = 'motor_1',
    ),
)

alias_config = {
    'motor_alias': {'motor_2': 100},
    }
