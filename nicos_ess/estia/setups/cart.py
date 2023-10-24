description = 'Motors for the metrology cart'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    mapproach=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Rotator for approach',
        motorpv=f'{pvprefix}m12',
        has_powerauto=False,
        fmtstr='%.1f',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mpos=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Cart positioning',
        motorpv=f'{pvprefix}m13',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mcart=device(
        'nicos.devices.generic.sequence.LockedDevice',
        description='Metrology Cart device',
        device='mpos',
        lock='mapproach',
        unlockvalue=60.,
        lockvalue=180.,
    ),
)
