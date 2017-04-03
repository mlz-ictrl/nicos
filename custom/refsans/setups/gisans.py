description = 'GISANS setup'

group = 'basic'

includes = ['vacuum', 'shutter', 'optic']


startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'k1'
"""
