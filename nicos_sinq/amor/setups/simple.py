description = 'AMOR reduced parameter choice'

group = 'basic'

includes = ['director_devices']

excludes = ['universal', 'deflector']

startupcode = '''
amor_director.mode = 'simple'
'''
