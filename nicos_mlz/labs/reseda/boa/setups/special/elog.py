description = 'setup for the electronic logbook'
group = 'special'

# If you want to use the electronic logbook, make sure the "system" setup has
# also a cache configured.

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText'],
        prefix = 'logbook/',
        cache = 'localhost',
    ),
)
