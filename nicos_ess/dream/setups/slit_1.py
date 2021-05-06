description = 'The split arrangement with 4 motors'
prefix = "IOC"

devices = dict(
    blade_l=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        unit='mm',
        epicstimeout=3.0,
        precision=0.1,
        description='X axis alignment',
        motorpv=f'{prefix}:m4',
    ),
    blade_r=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        unit='mm',
        epicstimeout=3.0,
        precision=0.1,
        description='Y axis alignment',
        motorpv=f'{prefix}:m5',
    ),
    blade_t=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        unit='mm',
        epicstimeout=3.0,
        precision=0.1,
        description='Z axis alignment',
        motorpv=f'{prefix}:m6',
    ),
    blade_b=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        unit='mm',
        epicstimeout=3.0,
        precision=0.1,
        description='Z axis alignment',
        motorpv=f'{prefix}:m7',
    ),
    slit_1=device('nicos.devices.generic.slit.Slit',
        description='Slit 1 with left, right, bottom and top motors',
        opmode='centered',
        left='blade_l',
        right='blade_r',
        top='blade_t',
        bottom='blade_b',
        ),
)
