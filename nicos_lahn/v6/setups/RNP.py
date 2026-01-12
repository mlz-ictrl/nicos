description = 'Polarized Neutron reflectometry (RNP) mode'

group = 'basic'

includes = [
    'beamstop_m',
    'monochromator_1',
    'slit1_1',
    'polarizer',
    'spinflipper1',
    'slit2_1',
    'sampletable_1',
    'beamstop_d',
    'slit3_1',
    'spinflipper2',
    'offspecularanalysator',
    'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to the RNP mode")
printinfo("======================================")
'''
