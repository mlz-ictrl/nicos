description = 'setup for the cache server'

group = 'special'

devices = dict(
    DB = device('nicos.services.cache.server.FlatfileCacheDatabase',
        storepath = configdata('config_data.cachepath'),
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = configdata('config_data.bind'),
        loglevel = 'info',
    ),
)
