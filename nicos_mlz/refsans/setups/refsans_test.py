description = 'Setup to test some components (only used during dev phase)'

group = 'basic'

includes = ['nok5a', 'sample']

startupcode = """
# set offsets of the blades ...
# for d in [zb1, zb2, ... ]:
#    d.mask = 'slit'
"""
