description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device('nicos.services.elog.handler.eworkbench.Handler',
        url = 'localhost',
        port = 5672,
        virtual_host = '/',
        username = 'guest',
        password = secret('eln_rabbitmq_password', default='guest'),
        static_queue = 'xrr-workbench',
    ),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText', 'LogbookWorkbench'],
        cache = 'localhost',
    ),
)
