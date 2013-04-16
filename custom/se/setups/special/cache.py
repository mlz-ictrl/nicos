description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/var/cache/nicos',
                    loglevel = 'info'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB',
                    server = 'localhost',
                    loglevel = 'info'),
)
