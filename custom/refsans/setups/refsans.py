description = 'REFSANS basic setup'

group = 'basic'

includes = ['vacuum', 'shutter', 'tube', 'guidehall', 'reactor', 'fak40',
            'optic', 'poti_ref', 'nl2b',
            'pumpstand', 'memograph',
            'sample',
            'room',
            'table',
            ]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
