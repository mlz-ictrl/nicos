description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator_2',
            'monochromator', 'monochromator_exchange', 'connecting_arms',
            'sampletable', 'detector']

startupcode = '''
read()
printinfo("======================================")
printinfo("Welcome to ANDES tension scanner setup")
printinfo("======================================")
'''
