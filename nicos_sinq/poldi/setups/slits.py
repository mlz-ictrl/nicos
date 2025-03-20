description = 'POLDI slits'

pvpref = 'SQ:POLDI:turboPmac1:'

devices = dict(
    d1hl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 1 (horizontal) left',
        motorpv = pvpref + 'D1HL',
    ),
    d1hr = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 1 (horizontal) right',
        motorpv = pvpref + 'D1HR',
    ),
    d2hl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 (horizontal) left',
        motorpv = pvpref + 'D2HL',
    ),
    d2hr = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 (horizontal) right',
        motorpv = pvpref + 'D2HR',
    ),
    d2vu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 (vertical) upper',
        motorpv = pvpref + 'D2VU',
    ),
    d2vl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 (vertical) lower',
        motorpv = pvpref + 'D2VL',
    ),
    d2x = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 X translation',
        motorpv = pvpref + 'D2X',
    ),
)
