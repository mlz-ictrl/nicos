description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/kompass',
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'kompassctrl.kompass.frm2',
        forwarders = ['GlobalCache'],
        keyfilters = ['stt.*', 'mtt.*'],
    ),
)
