description = 'Monochromator devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motb:'

devices = dict(
    mom=device('nicos_mlz.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Tilt monochromator motor',
               motorpv=pvprefix + 'mom',
               ),
    moz=device('nicos_mlz.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator z position of rotation axis motor',
               motorpv=pvprefix + 'moz',
               ),
    mtz=device('nicos_mlz.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator z position relative to rotation axis motor',
               motorpv=pvprefix + 'mtz',
               ),
    mty=device('nicos_mlz.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Monochromator y position motor',
               motorpv=pvprefix + 'mty',
               ),
)
