description = 'Frame overlap devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    fom=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap tilt motor',
               motorpv=pvprefix + 'fom',
               ),
    ftz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap z position of rotation axis motor',
               motorpv=pvprefix + 'ftz',
               ),
)
