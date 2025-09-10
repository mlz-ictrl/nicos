# If you want to use the electronic logbook, make sure the "system" setup has
# also a cache configured.

description = 'setup for the electronic logbook'

group = 'special'

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText'],
        prefix = 'logbook/',
        cache = configdata('config_data.cache_host'),
    ),
)
