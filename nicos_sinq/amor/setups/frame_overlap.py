description = 'Frame overlap devices in the SINQ AMOR.'

group='lowlevel'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    fom=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap tilt motor',
               motorpv=pvprefix + 'fom',
               errormsgpv=pvprefix + 'fom-MsgTxt',
               ),
    ftz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Frame overlap z position of rotation axis motor',
               motorpv=pvprefix + 'ftz',
               errormsgpv=pvprefix + 'ftz-MsgTxt',
               ),
)
