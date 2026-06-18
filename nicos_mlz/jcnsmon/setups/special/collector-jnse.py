description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/jnse',
        keyfilters = ['magb*.*', 'cooling.*', 'selector.*'],
    ),
    InfluxDB = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14871',
        prefix = 'nicos/jnse',
        keyfilters = ['magb*.*', 'cooling.*', 'selector.*'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.j-nse.frm2',
        forwarders = ['GlobalCache', 'InfluxDB'],
    ),
)
