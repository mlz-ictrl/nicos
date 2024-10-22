description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = '/data/cache',
        loglevel = 'info',
        makelinks = 'none',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        #server = 'kfes31.troja.mff.cuni.cz:8080',
        server = 'localhost',
        loglevel = 'info',
    ),
)
