description = 'Devices for the normal SANS sample holder'

pvprefix = 'SQ:SANS:turboPmac1:'

excludes = ['emagnet_sample']

devices = dict(
    z = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Table Height',
        motorpv = pvprefix + 'z',
    ),
    xo = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Table X Translation',
        motorpv = pvprefix + 'xo',
    ),
    yo = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Table Y Translation',
        motorpv = pvprefix + 'yo',
    ),
    a3 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table Rotation',
        motorpv = pvprefix + 'a3',
    ),
    xu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample Upper X Translation',
        motorpv = pvprefix + 'xu',
    ),
    sg = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table Rotation',
        motorpv = pvprefix + 'sg',
    ),
    spos = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample Position',
        motorpv = 'SQ:SANS:mota:spos',
        errormsgpv = 'SQ:SANS:mota:spos-MsgTxt',
        precision = 0.01,
    )
)
