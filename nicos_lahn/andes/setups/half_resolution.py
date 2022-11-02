description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator',
            'monochromator_2', 'exchange_2', 'connecting_arms_2',
            'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to ANDES half resolution setup")
printinfo("======================================")
'''
