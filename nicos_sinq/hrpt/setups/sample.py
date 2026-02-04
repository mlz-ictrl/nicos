description = 'Sample devices in the SINQ HRPT.'

pvprefix = 'SQ:HRPT:motc:'

devices = dict(
    som = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample omega motor',
        motorpv = pvprefix + 'SOM',
        errormsgpv = pvprefix + 'SOM-MsgTxt',
        precision = 0.01,
    ),
    som_oscillation = device('nicos.devices.generic.Oscillator',
        description = 'Sample oscillation',
        moveable = 'som',
        range = (-10, 10),
    ),
    chpos = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample Changer Position',
        motorpv = pvprefix + 'CHPOS',
        errormsgpv = pvprefix + 'CHPOS-MsgTxt',
        precision = 0.01,
    ),
    stx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample Table X Translation',
        motorpv = pvprefix + 'STX',
        errormsgpv = pvprefix + 'STX-MsgTxt',
        precision = 0.01,
    ),
    sty = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample table y translation',
        motorpv = pvprefix + 'STY',
        errormsgpv = pvprefix + 'STY-MsgTxt',
        precision = 0.01,
    )
)
