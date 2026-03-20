description = 'setup for the HTML status monitor'
group = 'special'

_detcolumn = Row(
    Block(
        'detector trolley', [
            BlockRow(
                Field(name = 'detx (along beam)', dev = 'detx', width = 20),
            ),
            BlockRow(
                Field(name = 'dety (perp beam)', dev = 'dety', width = 20),
            ),
            BlockRow(
                Field(name = 'detphi', dev = 'detphi', width = 20),
            ),
        ],
    ),
)

_bscolumn = Row(
    Block(
        'beam stop', [
            BlockRow(
                Field(name = 'bsx', dev = 'bsx', width = 20),
            ),
            BlockRow(
                Field(name = 'bsy', dev = 'bsy', width = 20),
            ),
            BlockRow(
                Field(name = 'bs (in/out)', dev = 'bs', width = 20),
            ),
            BlockRow(
                Field(name = 'bs type', dev = 'bsc', width = 20),
            ),
        ],
    ),
)

_live = Column(
    Block(
        'Live image of Detector',
        [
            BlockRow(
                Field(
                    name = 'Data (lin)',
                    picture = './live_lin.png',
                    width = 32,
                    height = 32,
                ),
                Field(
                    name = 'Data (log)',
                    picture = './live_log.png',
                    width = 32,
                    height = 32,
                ),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = '',
#        filename = '/afs/psi.ch/project/sinq/sinqstatus/sans1/detector.html',
	filename = '/home/sans/data/html/detector.html',
        interval = 10,
        loglevel = 'info',
        cache = 'localhost',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Moni',
        fontsize = 12,
        padding = 3,
        layout = [
            [_detcolumn,_bscolumn],
            [_live],
        ],
	expectmaster=False,
        noexpired = True,
    ),
)
