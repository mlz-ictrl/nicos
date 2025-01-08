description = 'Rotation RF'

pvprefix = 'SQ:BOA:mcu2:'

devices = dict(
    rf = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'RR rotation',
        motorpv = pvprefix + 'RF',
        errormsgpv = pvprefix + 'RF-MsgTxt',
        can_disable = True,
    ),
)
