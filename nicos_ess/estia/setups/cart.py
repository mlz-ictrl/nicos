description = 'Motors for the metrology cart'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    mapproach = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Rotator for approach',
        motorpv = f'{pvprefix}m12',
        errormsgpv = f'{pvprefix}m12-MsgTxt',
        errorbitpv = f'{pvprefix}m12-Err',
        reseterrorpv = f'{pvprefix}m12-ErrRst',
        unit = 'deg',
        fmtstr = '%.1f',
    ),
    mpos = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Cart positioning',
        motorpv = f'{pvprefix}m13',
        errormsgpv = f'{pvprefix}m13-MsgTxt',
        errorbitpv = f'{pvprefix}m13-Err',
        reseterrorpv = f'{pvprefix}m13-ErrRst',
    ),
    mcart = device('nicos.devices.generic.sequence.LockedDevice',
        description = 'Metrology Cart device',
        device = 'mpos',
        lock = 'mapproach',
        unlockvalue = 60.,
        lockvalue = 180.,
    ),
)
