description = 'Optics alignment devices in the SINQ NEUTRA.'

no_prefix = 'SQ:NEUTRA:optics:'

devices = dict(
    taz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Optics Z motor',
        motorpv = f'{no_prefix}taz',
        errormsgpv = f'{no_prefix}taz-MsgTxt',
    ),
)
