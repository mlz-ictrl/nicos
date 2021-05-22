description = 'AMOR unpolarized non-deflected beam configuration'

group = 'basic'

includes = [
    'chopper',
    'counter',
    'detector',
    'frame_overlap',
    'sample',
]

startupcode = '''
Exp.mode = 'horizontal'
'''
