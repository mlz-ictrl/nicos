description = 'Devices for the first detector assembly'

pvpref = 'SQ:ZEBRA:mcu3:'

excludes = ['wagen2']

devices = dict(
    nu = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Detector tilt',
        motorpv = pvpref + 'A4T',
        errormsgpv = pvpref + 'A4T-MsgTxt',
        precision = 0.01,
        unit = 'degree',
        can_disable = True,
    ),
    detdist = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Detector distance',
        motorpv = pvpref + 'W1DIST',
        errormsgpv = pvpref + 'W1DIST-MsgTxt',
        precision = 0.1,
        can_disable = True,
    ),
    ana = device('nicos.devices.generic.mono.Monochromator',
        description = 'Dummy analyzer for TAS mode',
        unit = 'meV'
    ),
)
startupcode = """
counts._setROParam('readpv', 'SQ:ZEBRA:counter.S3')
"""
