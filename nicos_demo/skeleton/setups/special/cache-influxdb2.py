description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDB2CacheDatabase',
        url = 'http://localhost:8086',
        org = 'organization_name',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'localhost',
        loglevel = 'info',
    ),
)
