description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText'],
        cache = 'tofhw.toftof.frm2.tum.de',
    ),
)
