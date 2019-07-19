description = 'setup for the astrium chopper'

group = 'optional'

devices = dict(
    chopper_dru_rpm = device('nicos.devices.generic.VirtualMotor',
        description = 'Chopper speed control',
        abslimits = (0, 20000),
        unit = 'rpm',
        fmtstr = '%.0f',
        maxage = 35,
    ),
    chopper_watertemp = device('nicos.devices.generic.ManualMove',
        description = 'Chopper water temp',
        unit = 'degC',
        fmtstr = '%.3f',
        maxage = 35,
        abslimits = (0, 100),
    ),
    chopper_waterflow = device('nicos.devices.generic.ManualMove',
        description = 'Chopper water flow',
        unit = 'l/min',
        fmtstr = '%.3f',
        maxage = 35,
        abslimits = (0, 100),
    ),
    chopper_vacuum = device('nicos.devices.generic.ManualMove',
        description = 'Chopper vacuum pressure',
        unit = 'mbar',
        fmtstr = '%.3f',
        maxage = 35,
        abslimits = (0, 100),
    ),
)

for i in range(1, 3):
    devices['chopper_ch%i_gear' % i] = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel %i gear' % i,
        fmtstr = '%.3f',
        maxage = 35,
        abslimits = (0, 10),
        unit = '',
    )
    devices['chopper_ch%i_phase' % i] = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel %i phase' % i,
        fmtstr = '%.3f',
        abslimits = (0, 10),
        maxage = 35,
        unit = '',
    )
    devices['chopper_ch%i_parkingpos' % i] = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel %i parking position' % i,
        fmtstr = '%.3f',
        abslimits = (0, 10),
        maxage = 35,
        unit = '',
    )
    devices['chopper_ch%i_speed' % i] = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel %i speed' % i,
        fmtstr = '%.3f',
        abslimits = (0, 10),
        maxage = 35,
        unit = '',
    )
