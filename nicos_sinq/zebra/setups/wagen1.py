description = 'Devices for the first detector assembly'

pvpref = 'SQ:ZEBRA:mcu3:'

excludes = ['wagen2']

devices = dict(
    nu = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector tilt',
        motorpv = pvpref + 'A4T',
        errormsgpv = pvpref + 'A4T-MsgTxt',
        precision = 0.01,
    ),
    detdist = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector distance',
        motorpv = pvpref + 'W1DIST',
        errormsgpv = pvpref + 'W1DIST-MsgTxt',
        precision = 0.1,
    ),
    ana = device('nicos.devices.generic.mono.Monochromator',
        description = 'Dummy analyzer for TAS mode',
        unit = 'meV'
    ),
)
