description = 'setup for the cache server'

group = 'special'

devices = dict(
    DB     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/users/cache',
                    loglevel = 'info',
                   ),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB',
                    server = 'tofhw.toftof.frm2',
                    loglevel = 'info',
                   ),
)
