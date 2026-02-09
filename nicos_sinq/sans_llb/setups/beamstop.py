description = 'Motors used to move the beamstop on the small angle detector'

pvprefix = 'SQ:SANS-LLB:turboPmac3:'

group = 'lowlevel'

devices = dict(
    bsx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Beamstop horizontal translation',
        motorpv = pvprefix + 'bsx',
    ),
    bsy = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Beamstop vertical translation',
        motorpv = pvprefix + 'bsy',
    ),
)
