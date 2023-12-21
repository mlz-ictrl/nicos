description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDBCacheDatabase',
        # localhost if influxdb runs on the same machine
        url = 'http://localhost:8086',
        # token of a password saved using nicos-kyestore
        keystoretoken = 'influxdb',
        org = 'organization_name',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'localhost',
        loglevel = 'info',
    ),
)
