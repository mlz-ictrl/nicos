description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device('nicos_mlz.devices.elog.eworkbench.Handler',
        url = 'localhost',
        port = 5672,
        virtual_host = '/',
        username = 'guest',
        password = secret('eln_rabbitmq_password', default='guest'),
        static_queue = 'toftof-workbench',
    ),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText', 'LogbookWorkbench'],
        cache = 'tofhw.toftof.frm2.tum.de',
    ),
)
