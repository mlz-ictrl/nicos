description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/dns',
        keyfilters = ['selector.*', 'cooling.*', 'chopper.*'],
    ),
    InfluxDB = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14871',
        prefix = 'nicos/dns',
        keyfilters = ['selector.*', 'cooling.*', 'chopper.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.dns.frm2',
        forwarders = ['GlobalCache', 'InfluxDB'],
    ),
)
