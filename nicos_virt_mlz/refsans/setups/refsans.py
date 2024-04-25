description = 'Virtual REFSANS basic setup'

group = 'basic'

includes = [
    'autocollimator',
    # 'b3h3',
    'backguard',
    'beamstop',
    # 'chamber',
    'chopper',
    # 'chopperphasentiming',
    'detector',
    # 'fak40',
    'gonio',
    'gonio_top',
    # 'guidehall',
    # 'h2',
    # 'height',
    # 'memograph',
    'nl2b',
    'optic_elements',
    # 'poti_ref',
    # 'prim_monitor',
    # 'pumpstand',
    # 'qmesydaq',
    'reactor',
    'resolution',
    # 'safedetectorsystem',
    # 'safetysystem',
    # 'sample',
    'samplechanger',
    'shutter',
    'shutter_gamma',
    # 'vsd',
    #  'vacuum',
    #  'instrument_mode',
    'qmesydaq',
    'alphai',
    'd_last_slit_sample',
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
)

startupcode = '''
alphai.userlimits = (0, 3.5)
'''
