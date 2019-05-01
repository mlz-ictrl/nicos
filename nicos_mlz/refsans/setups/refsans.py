description = 'REFSANS basic setup'

group = 'basic'

includes = [
    # 'vacuum', readout (hardware) defect MP 02.05.2018 09:13:28
    'shutter',
    'shutter_gamma',
    'guidehall',
    'reactor',
    'fak40',
    'chopper',
    'optic_elements',
    'h2',
    'poti_ref',
    'nl2b',
    'vsd',
    'pumpstand',
    'memograph',
    'sample',
    'detector',
]

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
