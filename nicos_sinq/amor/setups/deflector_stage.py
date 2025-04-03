description = 'Lift and pitch of deflector and flight tube'

display_order = 40

pvprefix = 'SQ:AMOR:masterMacs1:'

devices = dict(
    ltz_r = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Lift (z translation) of deflector & flight tube',
        motorpv = pvprefix + 'ltz',
        unit = 'mm',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    lom_r = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Tilt (pitch) of deflector & flight tube',
        motorpv = pvprefix + 'lom',
        unit = 'deg',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)