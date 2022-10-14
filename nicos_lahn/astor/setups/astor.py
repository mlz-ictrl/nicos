description = 'ASTOR setup'

group = 'basic'

includes = ['shutters', 'collimator', 'small_beam_limiter', 'filter', 'detector_translation']

startupcode = '''
read()
printinfo("================")
printinfo("Welcome to ASTOR")
printinfo("================")
'''
