description = 'Sample devices in the SINQ AMOR.'

display_order = 51

pvprefix = 'SQ:AMOR:masterMacs1:'

includes = ['base']

devices = dict(
    som = device('nicos_sinq.devices.epics.motor.SinqMotor',
                 description = 'Sample omega rotation',
                 motorpv = pvprefix + 'som',
                 visibility = ('metadata', 'namespace'),
                 ),
    soz = device('nicos_sinq.devices.epics.motor.SinqMotor',
                 description = 'Sample z lift (below omega and chi rotation)',
                 motorpv = pvprefix + 'soz',
                 visibility = ('metadata', 'namespace'),
                 ),
    )

alias_config = {
    'sah': {'s_zoffset': 20},
    'sample_height': {'s_zoffset': 20},
    }
