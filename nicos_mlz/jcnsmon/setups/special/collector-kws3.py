description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    #SECache = device('nicos.services.collector.CacheForwarder',
    #    cache = 'localhost',
    #    prefix = 'nicos/se',
    #),
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/kws3',
        keyfilters = ['selector.*', 'cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.kws3.frm2',
        forwarders = ['GlobalCache'],
    ),
)
