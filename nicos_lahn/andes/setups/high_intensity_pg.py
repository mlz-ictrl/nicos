description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator',
            'monochromator_4', 'exchange_3', 'connecting_arms_2',
            'detector']

startupcode = '''
read()
printinfo("========================================")
printinfo("Welcome to ANDES high intensity PG setup")
printinfo("========================================")
'''
