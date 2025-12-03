description = 'AMOR reduced parameter choice'

group = 'basic'

includes = ['base', 'deflector_stage']

excludes = ['simple', 'universal', 'qz']

alias_config = {
        'kappa': {'kap': 100},
        'sah': {'s_zoffset': 10},
        'sample_height': {'s_zoffset': 10},
        }

startupcode = '''
if 'som' in locals():
    fix(som, 'Cannot move with filled trough')
if 'sample_roll' in locals():
    fix(sample_roll, 'Cannot move with filled trough')
'''
