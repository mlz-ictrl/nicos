description = 'setup for the cache server'
group = 'special'
import os

devices = dict(
    DB = device('nicos.services.cache.server.FlatfileCacheDatabase',
        description = 'On disk storage for Cache Server',
        storepath =  os.environ.get('NICOSDUMP','.') + '/hrpt/cache',
        loglevel = 'info',
    ),
    Server=device('nicos.services.cache.server.CacheServer',
                  db='DB',
                  server='',
                  loglevel='info',
                  ),
)
