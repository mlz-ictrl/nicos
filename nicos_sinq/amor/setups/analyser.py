description = 'Analyser devices in the SINQ AMOR.'

includes = ['logical_motors']

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    aom=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Analyser tilt motor',
               motorpv=pvprefix + 'aom',
               errormsgpv=pvprefix + 'aom-MsgTxt',
               ),
    aoz=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Analyser z position of rotation axis motor',
               motorpv=pvprefix + 'aoz',
               errormsgpv=pvprefix + 'aoz-MsgTxt',
               ),
    atz=device('nicos.devices.epics.pyepics.motor.EpicsMotor',
               description='Analyser z position relative to rotation axis motor',
               motorpv=pvprefix + 'atz',
               errormsgpv=pvprefix + 'atz-MsgTxt',
               ),
)
