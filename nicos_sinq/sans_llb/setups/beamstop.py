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
    beamstop = device('nicos_sinq.sans_llb.devices.beamstop.Beamstop',
        description = 'Device to Change In-Position Beamstop',
        pvprefix = 'SQ:SANS-LLB:SPS-BEAMSTOP',
    ),
    beamstopcontroller = device('nicos_sinq.sans_llb.devices.beamstop.BeamstopMotorController',
        description = 'Ensures that the beamstop motors and changers can not be used simultaneously',
        beamstop = 'beamstop',
        bsx = 'bsx',
        bsy = 'bsy',
        visibility = (),
    ),
)
