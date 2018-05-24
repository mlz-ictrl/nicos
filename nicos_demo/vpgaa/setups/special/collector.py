description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = 'localhost:14716',
        prefix = 'nicos/demosys/',
    ),
    Webhook = device('nicos.services.collector.WebhookForwarder',
        hook_url = 'http://localhost:14444/receive',
        prefix = 'demo',
        http_mode = 'POST',
        paramencoding = 'json',
        keyfilters = ['.*/value'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'localhost:14869',
        forwarders = ['GlobalCache', 'Webhook'],
    ),
)
