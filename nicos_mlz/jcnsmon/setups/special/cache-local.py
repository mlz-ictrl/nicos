# This setup file configures the nicos cache service.

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.server.FlatfileCacheDatabase',
        storepath = '/data/cache-local',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '0.0.0.0:14870',
        loglevel = 'info',
    ),
)
