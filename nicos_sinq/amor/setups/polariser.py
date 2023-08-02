description = 'Polariser devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    pz1 = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Polariser Z-translation 1',
        motorpv = pvprefix + 'pz1',
        errormsgpv = pvprefix + 'pz1-MsgTxt',
    ),
    pz2 = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Polariser Z-translation 2',
        motorpv = pvprefix + 'pz2',
        errormsgpv = pvprefix + 'pz2-MsgTxt',
    ),
)
