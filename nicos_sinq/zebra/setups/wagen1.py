description = 'Devices for the first detector assembly'

pvpref = 'SQ:ZEBRA:turboPmac3:'

excludes = ['wagen2']

devices = dict(
    nu = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Detector tilt',
        motorpv = pvpref + 'A4T',
    ),
    detdist = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Detector distance',
        motorpv = pvpref + 'W1DIST',
    ),
    ana = device('nicos.devices.generic.mono.Monochromator',
        description = 'Dummy analyzer for TAS mode',
        unit = 'meV'
    ),
)
startupcode = """
counts._setROParam('readpv', 'SQ:ZEBRA:counter.S3')
"""
