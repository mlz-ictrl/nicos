description = 'Yet another neutron grating interferometry setup'

pvprefix = 'SQ:ICON:masterMacsNgi:'

devices = dict(
    g0_lin = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'G0 translation',
        motorpv = pvprefix + 'g0-lin',
    ),
    g0_rot = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'G0 rotation',
        motorpv = pvprefix + 'g0-rot',
    ),
    g1_lin = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'G1 translation',
        motorpv = pvprefix + 'g1-lin',
    ),
    g1_rot = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'G1 rotation',
        motorpv = pvprefix + 'g1-rot',
    ),
    g2_rot = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'G2 rotation',
        motorpv = pvprefix + 'g2-rot',
    ),
    samtry = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample TR y translation',
        motorpv = pvprefix + 'samtry',
        encoder_type = None
    ),
    samtrx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample TR x translation',
        motorpv = pvprefix + 'samtrx',
        encoder_type = None
    ),
    samtrz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample TR z translation',
        motorpv = pvprefix + 'samtrz',
        encoder_type = None
    ),
)
