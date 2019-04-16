description = 'Virtual REFSANS basic setup'

group = 'basic'

includes = [
    'vacuum',
    'shutter',
    'shutter_gamma',
    # 'guidehall',
    'reactor',
    # 'fak40',
    'chopper',
    # 'instrument_mode',
    'optic_elements',
    # 'poti_ref',
    # 'nl2b',
    # 'pumpstand',
    # 'memograph',
    'sample',
    'det_pos',
]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
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
