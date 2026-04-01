description = 'Sample table with stz'

display_order = 52

pvprefix = 'SQ:AMOR:masterMacs1:'

includes = ['base', 'sample_stage']
excludes = ['smz_table']

devices = dict(
    stz = device('nicos_sinq.devices.epics.motor.SinqMotor',
                 description = 'Sample z lift (above omega and chi rotations)',
                 motorpv = pvprefix + 'stz',
                 visibility = ('devlist', 'metadata', 'namespace'),
                 valid_pos_after_reference = True,
                 ),
    )

alias_config = {
    'sah': {'stz': 100},
    'sample_height': {'stz': 100}
    }
