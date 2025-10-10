description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device('nicos_mlz.devices.elog.eworkbench.Handler',
        url = 'infra01.dev.cluster.jcns.frm2.tum.de',
        port = 32672,
        virtual_host = '/',
        username = 'workbench',
        password = secret('workbench'),
        static_queue = 'vpanda-workbench',
    ),
    Logbook = device('nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText', 'LogbookWorkbench'],
        cache = 'localhost',
    ),
)
