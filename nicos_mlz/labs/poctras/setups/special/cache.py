description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = '/control/cache/nicos',
        loglevel = 'info'
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '',
        loglevel = 'info'
    ),
)
