description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/kws1',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.kws1.frm2',
        forwarders = ['GlobalCache'],
        keyfilters = ['selector.*'],
    ),
)
