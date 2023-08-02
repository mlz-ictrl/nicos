description = 'Frame overlap devices in the SINQ AMOR.'

group='lowlevel'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    fom=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Frame overlap tilt motor',
               motorpv=pvprefix + 'fom',
               errormsgpv=pvprefix + 'fom-MsgTxt',
               ),
    ftz=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Frame overlap z position of rotation axis motor',
               motorpv=pvprefix + 'ftz',
               errormsgpv=pvprefix + 'ftz-MsgTxt',
               ),
)
