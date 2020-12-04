description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.server.FlatfileCacheDatabase',
        description = 'On disk storage for Cache Server',
        storepath = configdata('config.DATA_PATH') + 'cache',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '',
        loglevel = 'info',
    ),
)
