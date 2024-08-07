description = 'common definitions for virtual stress-spec instrument'

group = 'configdata'

instrument = 'stressi'
host = 'localhost'
daemon_bind = '' if host == 'localhost' else host
cache_bind = '' if host == 'localhost' else host
cache_host = host
dataroot = 'data'
cachepath = f'{dataroot}/cache'
logging_path = 'log'
authenticators = ['Auth']
