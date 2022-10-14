description = 'ANDES setup'

group = 'basic'

includes = ['shutters', 'horizontal_beam_delimiter', 'collimator',
            'monochromator_3', 'monochromator_exchange', 'connecting_arms_2',
            'sampletable', 'detector']

startupcode = '''
read()
printinfo("========================================")
printinfo("Welcome to ANDES high intensity Ge setup")
printinfo("========================================")
'''
