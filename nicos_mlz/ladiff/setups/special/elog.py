description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler',
                         plotformat = 'png'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device('nicos_mlz.devices.elog.eworkbench.Handler',
        url = 'localhost',
        port = 5672,
        virtual_host = '/',
        username = 'guest',
        password = secret('eln_rabbitmq_password', default='guest'),
        static_queue = 'ladiff-workbench',
    ),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText', 'LogbookWorkbench'],
        cache = 'ctrl.ladiff.frm2.tum.de',
    ),
)
