description = 'AMOR unpolarized deflected beam mode'

group = 'basic'

includes = [
    'chopper',
    'counter',
    'detector',
    'frame_overlap',
    'polariser',
    'sample',
]

startupcode = '''
Exp.mode = 'deflector'
'''
