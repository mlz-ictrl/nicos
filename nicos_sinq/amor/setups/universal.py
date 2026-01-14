description = 'individual movement of all devices'

group = 'basic'

includes = ['base']

startupcode = '''
if 'som' in locals():
    release(som)
if 'sample_roll' in locals():
    release(sample_roll)
'''
