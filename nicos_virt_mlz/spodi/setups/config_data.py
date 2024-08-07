description = 'common definitions for virtual spodi instrument'

group = 'configdata'

instrument = 'spodi'
host = 'localhost'
daemon_bind = '' if host == 'localhost' else host
cache_bind = '' if host == 'localhost' else host
cache_host = host
dataroot = 'data'
cachepath = f'{dataroot}/cache'
logging_path = 'log'
authenticators = ['Auth']
