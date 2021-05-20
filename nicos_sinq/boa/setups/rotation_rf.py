description = 'Rotation RF'

pvprefix = 'SQ:BOA:mcu2:'

devices = dict(
    rf = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'RR rotation',
        motorpv = pvprefix + 'RF',
        errormsgpv = pvprefix + 'RF-MsgTxt',
    ),
)
