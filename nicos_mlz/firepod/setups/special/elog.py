# If you want to use the electronic logbook, make sure the "system" setup has
# also a cache configured.

description = 'setup for the electronic logbook'

group = 'special'

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device('nicos_mlz.devices.elog.eworkbench.Handler',
        url = 'localhost',
        port = 5672,
        virtual_host = '/',
        username = 'guest',
        password = secret('eln_rabbitmq_password', default='guest'),
        static_queue = 'firepod-workbench',
    ),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText', 'LogbookWorkbench'],
        prefix = 'logbook/',
        cache = 'localhost',
    ),
)
