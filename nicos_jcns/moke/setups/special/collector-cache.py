description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    FFcache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14870',
        prefix = 'nicos/',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'localhost:14869',
        forwarders = ['FFcache'],
    ),
)

