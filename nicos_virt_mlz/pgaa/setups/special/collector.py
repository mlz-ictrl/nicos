description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    GlobalCache = device('nicos.services.collector.CacheForwarder',
        cache = configdata('config_data.cache_host') + ':14716',
        prefix = 'nicos/demosys/',
    ),
    Webhook = device('nicos.services.collector.WebhookForwarder',
        hook_url = 'http://' + configdata('config_data.host') + ':14444/receive',
        prefix = 'demo',
        http_mode = 'POST',
        paramencoding = 'json',
        keyfilters = ['.*/value'],
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = configdata('config_data.cache_host'),
        forwarders = ['GlobalCache', 'Webhook'],
    ),
)
