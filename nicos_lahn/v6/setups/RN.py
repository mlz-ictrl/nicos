description = 'Neutron reflectometry (RN) mode'

group = 'basic'

includes = [
    'beamstop_m',
    'monochromator_1',
    'slit1_1',
    'slit2_1',
    'sampletable_1',
    'beamstop_d',
    'slit3_1',
    'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to the RN mode")
printinfo("======================================")
'''
