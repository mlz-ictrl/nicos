description = 'Slit 4 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    d4v = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Slit 4 opening motor',
        motorpv = pvprefix + 'd4v',
    ),
    d4h = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Slit 4 z position (lower edge) motor',
        motorpv = pvprefix + 'd4h',
    ),
)
