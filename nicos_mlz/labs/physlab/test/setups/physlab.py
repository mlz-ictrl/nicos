
devices = dict(
    ca = device('nicos_mlz.labs.physlab.devices.coupled.CoupledMotor',
        maxis = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-100, 100),
            unit = 'deg',
        ),
        caxis = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-50, 50),
            unit = 'deg',
        ),
        unit = 'deg',
    ),
)
