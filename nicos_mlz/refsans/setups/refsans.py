description = 'REFSANS basic setup'

group = 'basic'

includes = [
    'vacuum',
    'shutter',
    'shutter_gamma',
    # 'tube',
    'guidehall',
    'reactor',
    'fak40',
    'chopper',
    # 'virtual_disc2_pos_6',
    'instrument_mode',
    'optic_elements',
    'poti_ref',
    'nl2b',
    # 'pumpstand',
    'memograph',
    'sample',
    # 'room',
    # 'table',
    # 'det_pivot',
    # 'det_table',
    # 'det_yoke',
    'det_pos',
]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
