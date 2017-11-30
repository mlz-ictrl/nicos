description = 'debug MP only'

group = 'basic'

includes = ['optic_x']

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
