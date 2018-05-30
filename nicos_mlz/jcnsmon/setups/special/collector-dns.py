description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/dns',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.dns.frm2',
        forwarders = ['GlobalCache'],
        keyfilters = ['selector.*'],
    ),
)
