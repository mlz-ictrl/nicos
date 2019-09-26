description = 'Prototype motors for the metrology cart'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    mapproach = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Rotator for approach',
        motorpv = pvprefix + 'm5',
        errormsgpv = pvprefix + 'm5-MsgTxt',
        errorbitpv = pvprefix + 'm5-Err',
        reseterrorpv = pvprefix + 'm5-ErrRst',
        unit = 'deg',
        fmtstr = '%.1f',
    ),
    mpos = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Cart positioning',
        motorpv = pvprefix + 'm6',
        errormsgpv = pvprefix + 'm6-MsgTxt',
        errorbitpv = pvprefix + 'm6-Err',
        reseterrorpv = pvprefix + 'm6-ErrRst',
    ),
    mcart = device('nicos.devices.generic.sequence.LockedDevice',
        description = 'Metrology Cart device',
        device = 'mpos',
        lock = 'mapproach',
        unlockvalue = 60.,
        lockvalue = 180.,
    ),
)
