description = 'setup for the NICOS collector service from 20T'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'kfes12.troja.mff.cuni.cz',
        prefix = 'nicos/twenty',
        keyfilters = ['b_*', 't_*', 'magnet_*', 'exp*', 'cv_*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'kfes64.troja.mff.cuni.cz',
        forwarders = ['SECache'],
        prefix = 'nicos/',
    ),
)
