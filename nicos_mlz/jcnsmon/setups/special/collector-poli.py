description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/se',
        keyfilters = ['.*ccm8v.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.poli.frm2',
        forwarders = ['SECache'],
    ),
)
