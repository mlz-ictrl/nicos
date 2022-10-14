description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator',
            'monochromator_2', 'monochromator_exchange', 'connecting_arms_2',
            'sampletable', 'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to ANDES half resolution setup")
printinfo("======================================")
'''
