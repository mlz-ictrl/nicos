description = 'AMOR reduced parameter choice'

group = 'basic'

includes = ['base', 'deflector_stage']

excludes = ['simple', 'universal', 'qz']

startupcode = '''
if 'som' in locals():
    fix(som, 'Cannot move with filled trough')
if 'sample_roll' in locals():
    fix(sample_roll, 'Cannot move with filled trough')
'''
