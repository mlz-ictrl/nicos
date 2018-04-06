description = 'REFSANS basic setup'

group = 'basic'

includes = [
    'vacuum',
    'shutter',
    'shutter_gamma',
    'guidehall',
    'reactor',
    'fak40',
    'chopper',
    'instrument_mode',
    'optic_elements',
    'poti_ref',
    'nl2b',
    'pumpstand',
    'memograph',
    'sample',
    'det_pos',
]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
