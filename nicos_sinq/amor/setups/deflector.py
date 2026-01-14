description = 'AMOR unpolarized deflected beam mode'

group = 'basic'

includes = ['director_devices']

excludes = ['simple', 'universal']

startupcode = '''
amor_director.mode = 'deflector'
'''
