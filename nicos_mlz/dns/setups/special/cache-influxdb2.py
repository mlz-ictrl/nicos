description = 'setup for the influxdb2 cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDB2CacheDatabase',
        url = 'http://localhost:8086',
        org = 'mlz',
        unbuffered = True,
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'localhost:14870',
        loglevel = 'info',
    ),
)
