description = 'Analyser devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    aom=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser tilt motor',
               motorpv=pvprefix + 'aom',
               errormsgpv=pvprefix + 'aom-MsgTxt',
               ),
    aoz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser z position of rotation axis motor',
               motorpv=pvprefix + 'aoz',
               errormsgpv=pvprefix + 'aoz-MsgTxt',
               ),
    atz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Analyser z position relative to rotation axis motor',
               motorpv=pvprefix + 'atz',
               errormsgpv=pvprefix + 'atz-MsgTxt',
               ),
)
