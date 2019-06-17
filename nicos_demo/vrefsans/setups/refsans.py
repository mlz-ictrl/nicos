description = 'Virtual REFSANS basic setup'

group = 'basic'

includes = [
    # 'autocollimator',
    # 'b3h3',
    'backguard',
    'beamstop',
    # 'chamber',
    'chopper',
    # 'chopperphasentiming',
    'detector',
    # 'fak40',
    'gonio',
    # 'gonio_top',
    # 'guidehall',
    # 'h2',
    # 'height',
    # 'memograph',
    # 'nl2b',
    'optic_elements',
    # 'poti_ref',
    # 'prim_monitor',
    # 'pumpstand',
    # 'qmesydaq',
    'reactor',
    # 'safedetectorsystem',
    # 'safetysystem',
    'sample',
    # 'samplechanger',
    'shutter',
    'shutter_gamma',
    # 'vsd',

    #  'vacuum',
    #  'instrument_mode',
    'qmesydaq',
    'alphai',
]

startupcode = """
"""

devices = dict(
    table = device('nicos.devices.generic.Axis',
        description = 'detector table inside tube',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (620, 11025),
            unit = 'mm',
        ),
        precision = 0.05,
    ),
    tube = device('nicos.devices.generic.VirtualMotor',
        description = 'tube Motor',
        abslimits = (-120, 1000),
        unit = 'mm',
    ),
    # alphai = device('nicos.devices.generic.VirtualMotor',
    #     description = 'theta',
    #     abslimits = (0, 3.5),
    #     unit = 'deg',
    #     speed = 0.1,
    # ),
    alphaf = device('nicos_mlz.refsans.devices.tube.DetAngle',
        description = 'gamma',
        tubeangle = 'tube_angle',
        tubepos = 'det_table',
        pivot = 'det_pivot',
        theta = 'gonio_theta',
    ),
)

startupcode = '''
alphai.userlimits = (0, 3.5)
'''
