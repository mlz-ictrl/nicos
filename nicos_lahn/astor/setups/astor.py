description = 'ASTOR setup'

group = 'basic'

modules = ['nicos.commands.imaging']

includes = ['shutters', 'collimator', 'filter', 'beam_limiter', 'sampletable', 'detector']

startupcode = '''
printinfo("Welcome to ASTOR.")
'''
