description = 'AMOR unpolarized non-deflected beam configuration'

group = 'basic'

includes = [
    'chopper',
    'counter',
    'detector',
    'frame_overlap',
    'sample',
    'slit1',
    'slit5'
]

startupcode = '''
Exp.mode = 'horizontal'
'''
