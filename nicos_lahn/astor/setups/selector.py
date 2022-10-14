description = 'velocity selector setup'

group = 'optional'

devices = dict(
    selector=device('nicos.devices.generic.VirtualMotor',
                    description='Astrium selector hardware',
                    abslimits=(3100, 21000),
                    unit='rpm',
                    curvalue=3100,
                    fmtstr='%.0f',
                    requires={'level': 'admin'},
                    speed=1000,
                    ),
)
