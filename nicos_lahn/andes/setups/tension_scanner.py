description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator_2',
            'monochromator', 'exchange', 'connecting_arms',
            'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to ANDES tension scanner setup")
printinfo("======================================")
'''
