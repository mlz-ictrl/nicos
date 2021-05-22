description = 'AMOR virtual STZ mode'

group = 'basic'

includes = [
    'detector',
    'polariser',
    'sample',
    'diaphragm1',
]

startupcode = '''
Exp.mode = 'virtual_stz'
'''
