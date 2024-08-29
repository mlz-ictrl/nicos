description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    Global = device('nicos.services.collector.CacheForwarder',
        cache = configdata('config_data.cache_host') + ':14716',
        prefix = 'nicos/demosys/',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = configdata('config_data.cache_host'),
        forwarders = ['Global'],
    ),
)
