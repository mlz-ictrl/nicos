description = 'Polariser devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    pz1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Polariser Z-translation 1',
        motorpv = pvprefix + 'pz1',
        errormsgpv = pvprefix + 'pz1-MsgTxt',
    ),
    pz2 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Polariser Z-translation 2',
        motorpv = pvprefix + 'pz2',
        errormsgpv = pvprefix + 'pz2-MsgTxt',
    ),
)
