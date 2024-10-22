description = 'setup for the NICOS collector service from PPMS14'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'kfes12.troja.mff.cuni.cz',
        prefix = 'nicos/ppms14',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'kfes2.troja.mff.cuni.cz',
        forwarders = ['SECache'],
        prefix = 'ppms14/',
    ),
)
