description = 'common definitions for virtual nectar instrument'

group = 'configdata'

instrument = 'nectar'
host = 'localhost'
daemon_bind = '' if host == 'localhost' else host
cache_bind = '' if host == 'localhost' else host
cache_host = host
dataroot = 'data/FRM-II'
cachepath = 'data/cache'
logging_path = 'log'
authenticators = ['Auth']
