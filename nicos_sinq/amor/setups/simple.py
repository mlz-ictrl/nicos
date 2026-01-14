description = 'reduced parameter set for (high intensity) specular reflectometry'

group = 'basic'

includes = ['base', 'qz', 'diaphragm4']

excludes = ['deflector_stage', 'trough', 'universal']

startupcode = '''
if 'som' in locals():
    release(som)
if 'sample_roll' in locals():
    release(sample_roll)
'''
