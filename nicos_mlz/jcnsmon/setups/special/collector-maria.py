description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/maria',
        keyfilters = ['selector.*', 'cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.maria.frm2',
        forwarders = ['GlobalCache'],
    ),
)
