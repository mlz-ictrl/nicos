description = 'REFSANS basic setup'

group = 'basic'

includes = [
    'beamstop',
    'chamber',
    'chopper',
    'chopperphasentiming',
    'det_pos',
    'fak40',
    'gonio',
    'guidehall',
    'h2',
    'memograph',
    'nl2b',
    'optic_elements',
    'poti_ref',
    'prim_monitor',
    'pumpstand',
    'qmesydaq',
    'reactor',
    'safedetectorsystem',
    'sample',
    'detector',
    'safetysystem',
    'shutter',
    'shutter_gamma',
    'vsd',
]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
