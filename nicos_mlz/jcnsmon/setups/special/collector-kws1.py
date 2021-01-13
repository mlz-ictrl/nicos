description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/se',
        keyfilters = ['.*ccm3a.*'],
    ),
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/kws1',
        keyfilters = ['selector.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.kws1.frm2',
        forwarders = ['GlobalCache', 'SECache'],
    ),
)
