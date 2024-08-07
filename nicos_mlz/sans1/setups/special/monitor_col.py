description = 'setup for the status monitor'
group = 'special'

_collimationcolumn = Column(
    SetupBlock('collimation'),
)



devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'SANS-1 status monitor',
        loglevel = 'info',
        cache = 'ctrl.sans1.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 15,  # 12
        padding = 0,  # 3
        layout = [
            Row(_collimationcolumn),
        ],
    ),
)
