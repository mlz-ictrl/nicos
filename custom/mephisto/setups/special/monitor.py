description = 'setup for the status monitor for MEPHISTO'
group = 'special'


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'MEPHISTO status monitor',
                     loglevel = 'info',
                     cache = 'mephistoctrl.mephisto.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 16,
                     padding = 5,
                     layout = [],
                    ),
)
