description = 'AMOR unpolarized deflected beam mode'

group = 'basic'

includes = [
    'chopper',
    'counter',
    'detector',
    'frame_overlap',
    'polariser',
    'sample',
    'slit1',
    'slit5'
]

startupcode = '''
Exp.mode = 'deflector'
'''
