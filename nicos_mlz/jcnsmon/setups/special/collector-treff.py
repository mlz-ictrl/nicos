description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/treff',
        keyfilters = ['cooling.*'],
    ),
    InfluxDB = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14871',
        prefix = 'nicos/treff',
        keyfilters = ['cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.treff.frm2',
        forwarders = ['GlobalCache', 'InfluxDB'],
    ),
)
