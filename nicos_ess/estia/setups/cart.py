description = 'Prototype motors for the metrology cart'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    mapproach=device('nicos_ess.devices.epics.motor.EpicsMotor',
                     epicstimeout=3.0,
                     description='Rotator for approach',
                     motorpv=pvprefix + 'm2',
                     errormsgpv=pvprefix + 'm2-MsgTxt',
                     unit='deg',
                     fmtstr='%.1f',
                     ),
    mpos=device('nicos_ess.devices.epics.motor.EpicsMotor',
                epicstimeout=3.0,
                description='Cart positioning',
                motorpv=pvprefix + 'm1',
                errormsgpv=pvprefix + 'm1-MsgTxt',
                ),
    mcart=device('nicos.devices.generic.sequence.LockedDevice',
                 description='Metrology Cart device',
                 device='mpos',
                 lock='mapproach',
                 unlockvalue=60.,
                 lockvalue=180.,
                 ),
)
