description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.server.FlatfileCacheDatabase',
        storepath = 'data/cache',
        loglevel = 'info',
    ),
    # DB = device('nicos.services.cache.database.influxdb.InfluxDBCacheDatabase',
    #     url = 'http://localhost:8086',
    #     keystoretoken = 'influxdb',
    #     org = 'organization_name',
    #     bucket = 'nicos-cache',
    #     loglevel = 'info',
    # ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'localhost',
        loglevel = 'info',
    ),
)
