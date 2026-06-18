description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/kompass',
    ),
    InfluxDB = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14871',
        prefix = 'nicos/kompass',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'kompassctrl.kompass.frm2',
        forwarders = ['GlobalCache', 'InfluxDB'],
        keyfilters = ['stt.*', 'mtt.*'],
    ),
)
