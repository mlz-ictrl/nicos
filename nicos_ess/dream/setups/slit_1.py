description = 'The split arrangement with 4 motors'
prefix = "IOC"

devices = dict(
    blade_l=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='X-axis alignment',
        motorpv=f'{prefix}:m4',
        pva=True,
        monitor=True,
    ),
    blade_r=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='Y-axis alignment',
        motorpv=f'{prefix}:m5',
        pva=True,
        monitor=True,
    ),
    blade_t=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='Z-axis alignment',
        motorpv=f'{prefix}:m6',
        pva=True,
        monitor=True,
    ),
    blade_b=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='Z-axis alignment',
        motorpv=f'{prefix}:m7',
        pva=True,
        monitor=True,
    ),
    slit_1=device(
        'nicos.devices.generic.slit.Slit',
        description='Slit 1 with left, right, bottom and top motors',
        opmode='centered',
        left='blade_l',
        right='blade_r',
        top='blade_t',
        bottom='blade_b',
    ),
)
