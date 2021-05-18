description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    Global = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14716',
        prefix = 'nicos/demosys/',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'localhost:14869',
        forwarders = ['Global'],
    ),
)
