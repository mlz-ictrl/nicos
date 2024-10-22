description = 'setup for the NICOS collector service from MATFUN'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.CacheForwarder',
        cache = 'kfes12.troja.mff.cuni.cz',
        prefix = 'nicos/matfun',
        #keyfilters = ['.*ccm8v.*', '.*ccm12v.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'kfes2.troja.mff.cuni.cz',
        forwarders = ['SECache'],
        prefix = 'matfun/',
    ),
)
