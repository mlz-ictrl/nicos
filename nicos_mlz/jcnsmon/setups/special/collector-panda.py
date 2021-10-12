description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/se',
        keyfilters = ['.*ccm8v.*', '.*ccm12v.*'],
    ),
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/panda',
        keyfilters = ['cooling.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.panda.frm2',
        forwarders = ['GlobalCache', 'SECache'],
    ),
)
