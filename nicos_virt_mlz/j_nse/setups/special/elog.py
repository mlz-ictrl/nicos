description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    LogbookHtml = device('nicos.services.elog.handler.html.Handler'),
    LogbookText = device('nicos.services.elog.handler.text.Handler'),
    LogbookWorkbench = device(
        'nicos_mlz.devices.elog.eworkbench.Handler',
        url = 'rabbitmq.rabbitmq-stage.svc.cluster.local',
        port = 5672,
        virtual_host = '/',
        username = 'workbench',
        password = secret('workbench'),
        static_queue = 'vjnse-workbench',
    ),
    Logbook = device(
        'nicos.services.elog.Logbook',
        handlers = ['LogbookHtml', 'LogbookText'],
        cache = 'localhost',
    ),
)
