description = 'Instrument shutter'
prefix = "IOC"

devices = dict(
    beam_monitor_1=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        description="Beam monitor continuous position feedback",
        motorpv=f'{prefix}:m8',
        abslimits=(-10, 10),
        unit='mm',
        speed=5.,
    ),
    beam_monitor_switch=device(
        'nicos.devices.generic.Switcher',
        description="Toggles between in and out of the beam",
        moveable="beam_monitor_1",
        mapping={
            'IN': 0,
            'OUT': 5,
        },
        precision=0.01,
    )
)
