# This setup file configures the nicos cache service.

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/home/jcns/data/cache',
                    loglevel = 'info',
                   ),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB',
                    server = 'localhost',
                    loglevel = 'info',
                   ),
)
