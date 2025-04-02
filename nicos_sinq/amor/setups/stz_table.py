description = 'Sample table with stz'

display_order = 51

pvprefix = 'SQ:AMOR:mmac1:'

excludes = ['smz_table']

devices = dict(
    stz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample z lift (above omega and chi rotations)',
        motorpv = pvprefix + 'stz',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)
