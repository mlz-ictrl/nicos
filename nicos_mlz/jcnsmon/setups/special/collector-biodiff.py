description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    #SECache = device('nicos.services.collector.CacheForwarder',
    #    cache = 'localhost',
    #    prefix = 'nicos/se',
    #    keyfilters = ['.*ccm3a.*'],
    #),
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/biodiff',
        keyfilters = ['selector.*', 'cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.biodiff.frm2',
        forwarders = ['GlobalCache'],
    ),
)
