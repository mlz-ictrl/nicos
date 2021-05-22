description = 'Sample devices in the SINQ AMOR.'

group = 'lowlevel'

pvprefix = 'SQ:AMOR:motserial:'

devices = dict(
    som = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample omega motor',
        motorpv = pvprefix + 'som',
        errormsgpv = pvprefix + 'som-MsgTxt',
    ),
    soz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample z lift of base motor',
        motorpv = pvprefix + 'soz',
        errormsgpv = pvprefix + 'soz-MsgTxt',
    ),
)
