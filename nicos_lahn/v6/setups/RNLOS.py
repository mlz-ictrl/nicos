description = 'Off-specular Liquid Neutron reflectometry (RNLOS) mode'

group = 'basic'

includes = [
    'beamstop_m',
    'monochromator_2',
    'befilter',
    'slit1_2',
    'slit2_2',
    'sampletable_2',
    'beamstop_d',
    'slit3_2',
    'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to the RNLOS mode")
printinfo("======================================")
'''
