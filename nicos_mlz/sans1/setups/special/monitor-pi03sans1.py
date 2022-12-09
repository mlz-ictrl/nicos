description = 'setup for the status monitor'
group = 'special'

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = True,
        title = 'SANS-1 status monitor',
        loglevel = 'info',
        cache = 'ctrl.sans1.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consola',
        fontsize = 20,#12
        padding = 0,#3
        layout = [],
    ),
)
