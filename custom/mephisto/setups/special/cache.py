description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/localhome/data/cache',
                    loglevel = 'info'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB',
                    server = 'mephisto17.office.frm2',
                    loglevel = 'info'),
)
