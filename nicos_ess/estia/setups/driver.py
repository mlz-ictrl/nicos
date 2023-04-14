description = 'Motors for Driver1'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    driver1_1_approach=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M8 Driver1-1 Approach',
        motorpv=f'{pvprefix}m8',
        errormsgpv=f'{pvprefix}m8-MsgTxt',
        errorbitpv=f'{pvprefix}m8-Err',
        reseterrorpv=f'{pvprefix}m8-ErrRst',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    driver1_2_approach=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M9 Driver1-2 Approach',
        motorpv=f'{pvprefix}m9',
        errormsgpv=f'{pvprefix}m9-MsgTxt',
        errorbitpv=f'{pvprefix}m9-Err',
        reseterrorpv=f'{pvprefix}m9-ErrRst',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    driver1_1_adjust=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M10 Driver1-1 Adjust',
        motorpv=f'{pvprefix}m10',
        errormsgpv=f'{pvprefix}m10-MsgTxt',
        errorbitpv=f'{pvprefix}m10-Err',
        reseterrorpv=f'{pvprefix}m10-ErrRst',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    driver1_2_adjust=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M11 Driver1-2 Adjust',
        motorpv=f'{pvprefix}m11',
        errormsgpv=f'{pvprefix}m11-MsgTxt',
        errorbitpv=f'{pvprefix}m11-Err',
        reseterrorpv=f'{pvprefix}m11-ErrRst',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
)
